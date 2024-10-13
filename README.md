# MyAIAgent - LangChain + Ollama

The PyQt6 application utilizes LangChain, LangGraph, LangSmith, and Ollama to implement an Advanced RAG system through the integration of Adaptive RAG, Corrective RAG, and Self-RAG techniques.

For information regarding the GraphState, RAG prompt, Router instruction, Document prompt, Document instruction, Answer
prompt, Answer instruction, Hallucination prompt, and Hallucination instruction utilized in this application, please
refer the Langchain's tutorial.
[Local RAG agent with LLaMA3](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_adaptive_rag_local/)

## Prerequisites

Before you begin, ensure you have met the following requirements:

1. Python:

   Make sure you have Python 3.10 or later installed. You can download it from the official Python website.


2. Model:

   Ensure you have the Ollama and Embedding models downloaded on your local machine.


3. API Key and Setting:

   * Langchain API Key
   * Langchain Endpoint : https://api.smith.langchain.com
   * Langchain tracing v2 : true
   * Langchain project : Your project name
   * Tavily API Key


4. IDE/Code Editor:

   Use an IDE or code editor of your choice. Popular options include PyCharm, VSCode, and Eclipse.


5. PlantUML:

   PlantUML is used for generating UML diagrams.

   Download PyCharm plugin or Xcode extension.

## Quick Install

1. Clone repository

```bash
git clone https://github.com/hyun-yang/MyAIAgent-LangChain.git
```

2. With pip:

```bash
pip install -r requirements.txt
```

3. Run main.py

```bash
python main.py
```

4. Configure API Key
    * Open 'Setting' menu and set LangChain/Tavily API key.
    * Click Router/ Document/ RAG/ Hallucination /Answer tabs, enter the prompts and instructions for each, and then save them. Refer **[Prompt / Instruction Sample]** section.  


5. Re-run main.py

```bash
python main.py
```

## Feature

1) Versatile File Handling
   * Supports a variety of file types, including Text, PDF, and Word, making it easy to work with different document
     formats.

2) Efficient Vector Data Storage
   * Utilize SKLearnVectorStore and FAISS for robust and efficient vector data storage solutions.

3) Advanced RAG System
   * Leverage an advanced RAG system that incorporates Adaptive RAG, Corrective RAG, and Self-RAG techniques for enhanced data retrieval.

4) Customizable Prompts and Instructions
   * Enhance user interaction by allowing the addition of various prompts and instructions tailored to specific tasks.

5) Diverse Embedding Model Support
   * Integrate a wide range of Hugging Face embedding models for versatile applications in natural language processing.

6) Ollama Model Compatibility
   * Work with multiple Ollama models to expand the functionality of your application.

7) Conversation History Management
   * Store and review Q/A history in an SQLite database for easy access to past Q/A. 


## PyTorch Installation

To utilize the GPU, you need to install a version of [PyTorch](https://pytorch.org/) that is compatible with your operating system and the CUDA version supported by your GPU.

If the PyTorch version is not installed correctly or if you do not have a GPU, it will operate in CPU mode, which is slower.

Please refer to the **Utility.get_torch_device** method in the util folder for more information.


## Ollama Model List

Ollama currently do not have a method to retrieve the list of supported models,
so you need to open the **settings.ini** file and add them manually as shown below.

If you are using Ollama, make sure to check the following three things:

1) Install [Ollama](https://ollama.com/).
2) Download the model you wish to use.
3) Open the settings.ini file and add the name of the model.

```
Open 'settings.ini' file then add model list.

...
[Ollama_Model_List]
llama3.2:3b-instruct-fp16=true
llama3.2:3b-text-fp16=true
gemma2:27b=true
...

```

## Embedding Model List

If you have an embedding model that you want to use, first download the model, then open the **setting.ini** file and
add it to the **[Embedding_Model_List]** section as shown below.

1) Download the embedding model you wish to use from [Hugging Face](https://huggingface.co/)
2) Open the settings.ini file and go to [Embedding_Model_List] section, add the name of the model.

```
If the embedding model ID includes the '/' character, you need to replace slash '/' with '%5C' 
since QSetting class doesn't not process this character correctly when saving.

For example :
Embedding model id : nomic-ai/nomic-embed-text-v1.5
then, add as follows
Setting ini : nomic-ai%5Cnomic-embed-text-v1.5=true

Embedding model id : BAAI/bge-m3
then, add as follows
Setting ini : BAAI%5Cbge-m3=true

...
[Embedding_Model_List]
nomic-ai%5Cnomic-embed-text-v1.5=true
BAAI%5Cbge-m3=true
BAAI%5Cbge-small-en=true
...

```

## Prompt / Instruction Sample

* Refer Langchain official tutorial [Local RAG agent with LLaMA3](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_adaptive_rag_local/)

* Router Prompt
```markdown
You are an expert at routing a user question to a vectorstore or web search.

The vectorstore contains documents related to agents, prompt engineering, and adversarial attacks.
 
Use the vectorstore for questions on these topics. For all else, and especially for current events, use web-search.

Return JSON with single key, datasource, that is 'websearch' or 'vectorstore' depending on the question.
```

* Document Prompt
```markdown
Here is the retrieved document: \n\n {document} \n\n 
Here is the user question: \n\n {question}. 

This carefully and objectively assess whether the document contains at least some information that is relevant to the question.

Return JSON with single key, binary_score, that is 'yes' or 'no' score to indicate whether the document contains at least some information 
that is relevant to the question.
```

* Document Instruction
```markdown
You are a grader assessing relevance of a retrieved document to a user question.

If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant.
```

* RAG Prompt
```markdown
You are an assistant for question-answering tasks. 

Here is the context to use to answer the question:

{context} 

Think carefully about the above context. 

Now, review the user question:

{question}

Provide an answer to this questions using only the above context. 

Answer:
```


* Hallucination Prompt
```markdown
FACTS: \n\n {documents} \n\n STUDENT ANSWER: {generation}. 

Return JSON with two two keys, binary_score is 'yes' or 'no' score to indicate whether the STUDENT ANSWER is grounded in the FACTS.

And a key, explanation, that contains an explanation of the score.
```


* Hallucination Instruction
```markdown
You are a teacher grading a quiz. 

You will be given FACTS and a STUDENT ANSWER. 

Here is the grade criteria to follow:

(1) Ensure the STUDENT ANSWER is grounded in the FACTS. 

(2) Ensure the STUDENT ANSWER does not contain "hallucinated" information outside the scope of the FACTS.

Score:

A score of yes means that the student's answer meets all of the criteria. This is the highest (best) score. 

A score of no means that the student's answer does not meet all of the criteria. This is the lowest possible score you can give.

Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. 

Avoid simply stating the correct answer at the outset.
```


* Answer Prompt
```markdown
QUESTION: \n\n {question} \n\n STUDENT ANSWER: {generation}. 

Return JSON with two two keys, binary_score is 'yes' or 'no' score to indicate whether the STUDENT ANSWER meets the criteria.

And a key, explanation, that contains an explanation of the score.
```


* Answer Instruction
```markdown
You are a teacher grading a quiz. 

You will be given a QUESTION and a STUDENT ANSWER. 

Here is the grade criteria to follow:

(1) The STUDENT ANSWER helps to answer the QUESTION

Score:

A score of yes means that the student's answer meets all of the criteria. This is the highest (best) score. 

The student can receive a score of yes if the answer contains extra information that is not explicitly asked for in the question.

A score of no means that the student's answer does not meet all of the criteria. This is the lowest possible score you can give.

Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. 

Avoid simply stating the correct answer at the outset.
```

### UML Diagram

* Main ClassDiagram



* MyDocumentModel Class Diagram



* LangchainWorkflowModel Sequence Diagram



## Screenshots


* Setting
  ![langchain_github_setting](https://github.com/user-attachments/assets/b894e4b3-3a7f-49de-b8c5-316c26ef6441)


* AI Agent - Document tab
  ![langchain_github_document](https://github.com/user-attachments/assets/f943c5a9-2d1d-4edd-9195-0258579fcca9)


* AI Agent - vector store
  ![langchain_github_vectorstore](https://github.com/user-attachments/assets/f53d5a79-efe2-4eee-957c-371394ced52b)


* AI Agent - websearch
  ![langchain_github_websearch_swarm](https://github.com/user-attachments/assets/153adacc-0c75-4f1e-b476-83fca1c27ef3)


* Agent QA List
  ![langchain_github_QA_list](https://github.com/user-attachments/assets/2ccae7d1-80b3-41b9-8e70-ff04d33e916a)


* Main Class Diagram
  ![langchain_github_main_class_uml](https://github.com/user-attachments/assets/0bc1a371-3ec6-4085-8d59-a94cd158f23d)


* MyDocumentModel Class Diagram
  ![mydocumentmodel_class_uml](https://github.com/user-attachments/assets/725656f9-e6a0-4e44-864c-ff37fbf11345)


* MyDocumentModel Sequence Diagram
  ![mydocumentmodel_sequence_uml](https://github.com/user-attachments/assets/9bd164dc-17dc-49ee-8888-dc3914435b4f)


* LangchainWorkflowModel Class/Sequence Diagram
  ![Langchainworkflow_uml](https://github.com/user-attachments/assets/7eaa7da4-781c-4b34-a7f0-cfc883626c44)


## License

Distributed under the MIT License.