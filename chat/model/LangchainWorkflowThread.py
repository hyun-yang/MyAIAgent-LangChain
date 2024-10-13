import json
import operator
import time
from pprint import pprint
from typing import List, Annotated

from PyQt6.QtCore import QThread, pyqtSignal
from langchain_community.tools import TavilySearchResults
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.constants import END
from langgraph.graph import StateGraph
from typing_extensions import TypedDict

from util.Constants import Constants, LANGCHAIN_CONSTANT
from util.Utility import Utility


class GraphState(TypedDict):
    """
    Graph state is a dictionary that contains information we want to propagate to, and modify in, each graph node.
    """
    question: str  # User question
    generation: str  # LLM generation
    web_search: str  # Binary decision to run web search
    max_retries: int  # Max number of retries for answer generation
    answers: int  # Number of answers generated
    loop_step: Annotated[int, operator.add]
    documents: List[str]  # List of retrieved documents


class LangchainWorkflowThread(QThread):
    response_signal = pyqtSignal(str, str)
    response_finished_signal = pyqtSignal(str, str, float, bool)

    def __init__(self, args):
        super().__init__()

        self.force_stop = False
        self.stream = True
        self.question = args['question']
        self.prompt_list = args['prompt_list']
        self.retriever = args["retriever"]
        self.llm_name = args["llm_name"]
        self.search_result = args["search_result"]
        self.max_retries = args["max_retries"]

        self.graph = None
        self.valid_source = None
        self.invalid_source = None
        self.final_response = {}

        self.llm = ChatOllama(model=self.llm_name, temperature=0)
        self.llm_json_mode = ChatOllama(model=self.llm_name, temperature=0, format='json')

        self.web_search_tool = TavilySearchResults(k=self.search_result)
        self.generate_workflow()

    def run(self):
        self.start_time = time.time()
        try:
            for graphstate in self.graph.stream(self.question, stream_mode="values"):
                pprint(graphstate)
                if 'generation' in graphstate and self.valid_source:
                    self.final_response['content'] = graphstate['generation'].content
                    self.final_response['model'] = graphstate['generation'].response_metadata['model']
                    self.final_response['done_reason'] = graphstate['generation'].response_metadata['done_reason']
                    self.handle_response(self.final_response)

                if 'generation' in graphstate and self.invalid_source:
                    self.response_signal.emit(LANGCHAIN_CONSTANT.MAX_RETRIES_REACHED, LANGCHAIN_CONSTANT.ERROR)
        except Exception as e:
            self.response_signal.emit(str(e), LANGCHAIN_CONSTANT.ERROR)

    def route_question(self, state):
        route_question = self.llm_json_mode.invoke(
            [SystemMessage(content=self.prompt_list['router_instruction'])] + [
                HumanMessage(content=state["question"])])
        source = json.loads(route_question.content)['datasource']

        if source == 'websearch':
            self.final_response["route_type"] = "websearch"
            return "websearch"
        elif source == 'vectorstore':
            self.final_response["route_type"] = "vectorstore"
            return "vectorstore"

    def retrieve(self, state):
        question = state['question']
        documents = self.retriever.invoke(question)
        return {"documents": documents}

    def grade_documents(self, state):
        question = state['question']
        documents = state['documents']

        # Score each doc
        valid_docs = []
        web_search = "No"

        for d in documents:
            doc_grader_prompt_formatted = self.prompt_list['doc_grader_prompt'].format(document=d.page_content,
                                                                                       question=question)
            doc_grader_instruction = self.prompt_list['doc_grader_instruction'].format(document=d.page_content,
                                                                                       question=question)
            result = self.llm_json_mode.invoke(
                [SystemMessage(content=doc_grader_instruction)] + [HumanMessage(content=doc_grader_prompt_formatted)])
            grade = json.loads(result.content)['binary_score']

            if grade.lower() == "yes":
                valid_docs.append(d)
            else:
                web_search = "Yes"
                continue
        return {"documents": valid_docs, "web_search": web_search}

    def decide_to_generate(self, state):
        web_search = state["web_search"]

        if web_search.lower() == "yes":
            self.final_response["route_type"] = "websearch"
            return "websearch"
        else:
            return "generate"

    def web_search(self, state):
        question = state['question']
        documents = state.get("documents", [])

        # Tavily Web search
        docs = self.web_search_tool.invoke({"query": question})
        web_results = "\n".join([d["content"] for d in docs])
        web_results = Document(page_content=web_results)
        documents.append(web_results)
        return {"documents": documents}

    def generate(self, state):
        question = state['question']
        documents = state['documents']
        loop_step = state.get('loop_step', 0)
        docs_txt = self.format_docs(documents)
        rag_prompt_formatted = self.prompt_list['rag_prompt'].format(context=docs_txt, question=question)
        generation = self.llm.invoke([HumanMessage(content=rag_prompt_formatted)])
        return {"generation": generation, "loop_step": loop_step + 1}

    def grade_generation_v_documents_and_question(self, state):
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]
        max_retries = self.max_retries

        hallucination_grader_prompt_formatted = self.prompt_list['hallucination_grader_prompt'].format(
            documents=self.format_docs(documents),
            generation=generation.content)
        result = self.llm_json_mode.invoke(
            [SystemMessage(content=self.prompt_list['hallucination_grader_instruction'])] + [
                HumanMessage(content=hallucination_grader_prompt_formatted)])
        grade = json.loads(result.content)['binary_score']

        if grade == "yes":
            answer_grader_prompt_formatted = self.prompt_list['answer_grader_prompt'].format(question=question,
                                                                                             generation=generation.content)
            result = self.llm_json_mode.invoke(
                [SystemMessage(content=self.prompt_list['answer_grader_instruction'])] + [
                    HumanMessage(content=answer_grader_prompt_formatted)])
            grade = json.loads(result.content)['binary_score']

            if grade == "yes":
                self.valid_source = True
                return "useful"
            elif state["loop_step"] <= max_retries:
                self.valid_source = False
                return "not useful"
            else:
                self.valid_source = False
                return "max retries"
        elif state["loop_step"] <= max_retries:
            self.invalid_source = True
            return "not supported"
        else:
            self.invalid_source = True
            return "max retries"

    def generate_workflow(self):
        self.workflow = StateGraph(GraphState)

        # Define the nodes
        self.workflow.add_node("websearch", self.web_search)
        self.workflow.add_node("retrieve", self.retrieve)
        self.workflow.add_node("grade_documents", self.grade_documents)
        self.workflow.add_node("generate", self.generate)

        # Build graph
        self.workflow.set_conditional_entry_point(
            self.route_question,
            {
                "websearch": "websearch",
                "vectorstore": "retrieve",
            }
        )

        self.workflow.add_edge("websearch", "generate")
        self.workflow.add_edge("retrieve", "grade_documents")
        self.workflow.add_conditional_edges(
            "grade_documents",
            self.decide_to_generate,
            {
                "websearch": "websearch",
                "generate": "generate",
            }
        )
        self.workflow.add_conditional_edges(
            "generate",
            self.grade_generation_v_documents_and_question,
            {
                "not supported": "generate",
                "useful": END,
                "not useful": "websearch",
                "max retries": END,
            }
        )
        self.graph = self.workflow.compile()

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def set_force_stop(self, force_stop):
        self.force_stop = force_stop

    def handle_response(self, response):
        if self.force_stop:
            self.finish_run(response.model, Constants.FORCE_STOP, self.stream)
        else:
            result = response['content']
            finish_reason = response['done_reason']
            model = response['model']
            self.response_signal.emit(Utility.base64_encode_bytes(self.graph.get_graph().draw_mermaid_png()), result)
            self.finish_run(model, finish_reason, self.stream)

    def finish_run(self, model, finish_reason, stream):
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        self.response_finished_signal.emit(model + " | " + self.final_response['route_type'], finish_reason,
                                           elapsed_time, stream)
