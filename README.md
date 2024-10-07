# Book-review-assistant

This repository contains a powerful Book Review Assistant application built using a Large Language Model (LLM). The assistant helps users generate comprehensive book reviews by analyzing key themes, characters, and plots from a provided book summary or input text. 

## 1. Problem Overview

Readers often struggle to select books that match their interests, preferences, or mood. With a vast range of genres, authors, and themes, finding the perfect book can be overwhelming. For example, a reader who enjoys historical fiction might not always know where to find books that mix history with a fast-paced narrative style. Similarly, a fan of science fiction may be looking for books that explore philosophical questions rather than action-driven plots, but identifying these nuances can be difficult.

Additionally, while there are book reviews, recommendations, and summaries available online, readers may not always have the time to sift through this vast information or may find it difficult to trust generic reviews. The need for personalized book recommendations, based on specific criteria such as genre, writing style, and previous reading history, is an ongoing challenge for readers.

For instance, a reader might say, "I loved The Night Circus by Erin Morgenstern for its magical realism and rich, immersive world-building. What other books might give me a similar experience?" In such cases, general recommendation systems may fall short in delivering nuanced suggestions, whereas a tool utilizing an LLM could provide more insightful recommendations. By considering a combination of factors—like writing style, themes of enchantment, or atmospheric storytelling—the LLM could suggest titles like The Starless Sea by the same author or Jonathan Strange & Mr Norrell by Susanna Clarke, with explanations for why each recommendation aligns with the reader's interests.

### 1.1. How LLMs Can Help?

Large Language Models (LLMs), such as GPT-based models, can play a significant role in addressing this problem by providing personalized, human-like recommendations based on user input. Here’s how LLMs offer value:

1. **Natural Language Understanding**: LLMs can interpret user queries expressed in everyday language. A user can simply describe their preferences—such as “I’m in the mood for a mystery novel with deep character development,” or “I loved the pacing in *The Da Vinci Code*, what should I read next?”—and the model can understand and generate appropriate suggestions.

2. **Contextual Recommendations**: Unlike simple recommendation engines that rely on predefined algorithms (e.g., "customers who bought X also bought Y"), LLMs can process vast amounts of textual information from multiple sources, such as book reviews, summaries, and author interviews. They can then offer recommendations that not only match the user’s specific request but also explain why a particular book would be a good fit based on the reader’s preferences.

3. **Summarizing Reviews and Content**: LLMs can process book reviews, synopses, and critical analyses, providing concise summaries for readers who want quick insights into a book without having to go through multiple reviews. This saves time and ensures that users can make informed decisions quickly.

4. **Enhanced Personalization**: LLMs can remember previous interactions (based on integration with a user’s profile) to deliver tailored recommendations over time. For example, if a reader has consistently shown interest in books with philosophical themes or specific authors, the LLM can incorporate this information into future recommendations.

5. **Engagement and Interaction**: LLMs can simulate conversations with users about their reading preferences. This allows for an interactive experience where users can ask follow-up questions, refine their preferences, and explore different genres or authors dynamically. For example, a reader might ask, “Is this book suitable for young adults?” or “How does this author compare to someone like George Orwell?”

_______________________________________________________________________________

## 2. Description of Solution

![architecture](media/Screenshot%20from%202024-10-07%2010-22-12.png)

This architecture aims to address the challenge of personalized book recommendations using a combination of open-source tools and machine learning models. The solution integrates various components that interact to process book review data, store embeddings, and utilize a large language model (LLM) to generate recommendations.

### 2.1. **Solution Architecture: Book Review Assistant**

#### **1. Dataset: Amazon Review Books (Kaggle)**
- **Purpose**: The dataset contains book reviews from Amazon, providing essential data points like ratings, review text, and user information.
- **Source**: The dataset will be downloaded from Kaggle, specifically the *amazon-review-books* dataset, which serves as the foundation for extracting valuable book-related insights.

#### **2. Python Script for Dataset Download**
- **Implementation**: A Python script is used to automate the download of the dataset from Kaggle. This script will authenticate with Kaggle’s API, retrieve the dataset, and prepare it for further processing.
- **Key Components**:
  - Kaggle API integration
  - Data preprocessing (e.g., filtering, removing null values)

#### **3. MinIO for Dataset Storage**
- **Purpose**: MinIO is used as an object storage solution to store the downloaded dataset. This setup allows scalable and efficient storage for large datasets.
- **Workflow**:
  - After the dataset is downloaded via the Python script, it is stored in MinIO buckets for further access.
  - MinIO acts as a highly available and S3-compatible storage backend.

#### **4. Python Script to Load Data into Elasticsearch**
- **Implementation**: A second Python script is created to read the dataset from MinIO and load the data into Elasticsearch. Each book review will be indexed as a document, and an embedding of the review text will be generated for later similarity searches.
- **Components**:
  - Elasticsearch’s Python client for inserting documents
  - Text embeddings generated using a pre-trained model like Sentence-BERT

#### **5. Elasticsearch for Document and Embedding Storage**
- **Purpose**: Elasticsearch will store both the original review text as well as the corresponding vector embeddings of the text. These embeddings will be used to perform similarity searches to find reviews that are contextually relevant to a user query.
- **Workflow**:
  - Review documents are indexed in Elasticsearch.
  - Text embeddings are stored alongside the documents, enabling semantic search functionalities.

#### **6. Flask API for Document Retrieval and Prompt Generation**
- **Purpose**: A Flask API is developed to interface with Elasticsearch and retrieve documents (reviews) that are closest to the user’s input query. The Flask API will also generate prompts for the LLM model to enhance recommendation quality.
- **Workflow**:
  - The API accepts a user query.
  - Retrieves the top relevant documents from Elasticsearch based on embedding similarity.
  - Forms a prompt using the retrieved documents to feed into the LLM.

#### **7. Ollama Container for LLM (Gemma2B Model)**
- **Purpose**: The Ollama container runs the Gemma2B model, an LLM specifically designed to handle text generation tasks. This model processes the prompt generated by the Flask API and outputs personalized book recommendations based on the extracted book reviews.
- **Workflow**:
  - The Flask API sends a formatted prompt to the LLM model running inside the Ollama container.
  - The model generates a response, which is presented as a personalized recommendation to the user.

#### **8. PostgreSQL for Metadata Storage**
- **Purpose**: PostgreSQL is used to store metadata related to user queries, recommendations, and system performance metrics.
- **Stored Data**:
  - User query history
  - LLM responses
  - Elasticsearch query metadata (e.g., search times, relevance scores)

#### **9. RAG (Retrieval-Augmented Generation) Evaluation with Prefect and Grafana**
- **Purpose**: Prefect is used for orchestrating the data pipelines and evaluation tasks, while Grafana monitors the overall system performance, specifically focusing on the quality of the RAG system.
- **Workflow**:
  - Prefect manages workflows such as dataset downloads, Elasticsearch indexing, and recommendation generation.
  - Grafana tracks and visualizes metrics like response times, recommendation quality (using custom evaluation metrics), and LLM accuracy in generating relevant suggestions.

### 2.2. **End-to-End Workflow:**
1. The dataset is downloaded from Kaggle and stored in MinIO.
2. A Python script loads the dataset from MinIO into Elasticsearch, storing both reviews and embeddings.
3. A user interacts with the Flask API, which retrieves the most relevant reviews based on similarity search.
4. The Flask API generates a prompt and sends it to the Gemma2B LLM model in the Ollama container.
5. The LLM generates a book recommendation based on the retrieved reviews.
6. The recommendation and system performance data are stored in PostgreSQL, and Prefect orchestrates workflow evaluations.
7. Grafana monitors the system’s RAG process to ensure optimal performance and recommendation accuracy.

_______________________________________________________________________________

## 3. Docker and Docker-compose

For this project, Docker and Docker Compose are used to virtualize the applications involved in the solution architecture. Each component, such as the Flask API, Elasticsearch, PostgreSQL, and Ollama container, is containerized using Docker. Docker Compose is then used to orchestrate and manage multiple containers, ensuring that all services run smoothly together in a consistent environment.

### 3.1. Advantages of Using Docker and Docker Compose

1. **Consistency Across Environments**: Docker ensures that the applications run the same way on any system, whether it’s a developer’s local machine or a cloud server. This reduces the "it works on my machine" problem by bundling dependencies and configurations within containers.

2. **Isolation**: Each component of the system runs in its own container, isolated from the others. This isolation allows you to run different versions of applications or services without conflicts, which is particularly useful when working with complex stacks like Elasticsearch, Flask, and PostgreSQL.

3. **Scalability**: Docker makes it easy to scale individual components. For example, if the Flask API needs more instances to handle higher traffic, Docker Compose can scale it horizontally by spinning up more API containers while keeping the rest of the system intact.

4. **Simplified Management with Docker Compose**: Docker Compose allows for defining and running multi-container Docker applications with a single command. It manages the dependencies, ensures that containers communicate with each other properly, and handles container lifecycles, making deployment and development easier.

5. **Portability**: Since Docker containers encapsulate the application and its environment, they can easily be moved and deployed to different systems, whether on-premises or in the cloud, without requiring reconfiguration.

6. **Resource Efficiency**: Containers use system resources more efficiently compared to traditional virtual machines. They share the host system’s kernel while still isolating applications, which reduces the overhead of running multiple services and speeds up development cycles.

_______________________________________________________________________________

## 4. Reproducitibility


### 2.1. Instructions to Start the Project

1. **Clone the Project Repository:**
   If you haven't already, clone the project repository to your local machine:
   ```bash
   git clone https://github.com/jelambrar96-datatalks/book-review-assistant.git
   cd book-review-assistant
   ```

2. **Set Up the Environment:**
   Ensure the `.env` file is in the project root directory. This file contains all the necessary environment variables. If it’s not already created, create it and copy the content provided above into the file.

   This is a example of `.env` file.

```bash
OLLAMA_KEY="ollama"

OPENAI_API_KEY="your_secret_openai_api_key"
OPENAI_MODEL="gpt-3.5-turbo"

KAGGLE_USERNAME="your_kaggle_username"
KAGGLE_KEY="your_kaggle_secret_key"

AWS_BUCKET_NAME="test"
AWS_ACCESS_KEY_ID="test_aws_access_key"
AWS_SECRET_ACCESS_KEY="test_secret_access_key"
```

3. **Build the Docker Images:**
   Some services require building Docker images from custom Dockerfiles. Use the following command to build those images:
   ```bash
   docker-compose build
   ```

4. **Start the Docker Containers:**
   To start all the services defined in the `docker-compose.yml` file, run:
   ```bash
   docker-compose up -d
   ```
   The `-d` flag runs the containers in detached mode, meaning they will run in the background.

5. **Verify All Services Are Running:**
   Use the following command to list all running containers and verify that everything started correctly:
   ```bash
   docker-compose ps
   ```

6. **Download model on ollama container:**
    Enter a ollama container, you need to get ollama container id using `docker-compose ps`:
    ```bash
    docker exec -it ollama_conainer_id /bin/bash
    ```
    download gemma 2b model:
    ```bash
    ollama pull gemma:2b
    ```

_______________________________________________________________________________

## 5. Retrieval

In my RAG (Retrieval-Augmented Generation) project using LLM, I implemented the vector embedding search technique for retrieval. This method converts documents and queries into dense vectors, which are then compared in high-dimensional space to identify the most relevant matches.

The advantages of vector embedding search include:

Semantic Understanding: Unlike keyword-based search, vector embeddings capture the meaning of words, allowing for more accurate retrieval based on context rather than exact matches.
Efficiency with Large Datasets: Embedding search can handle vast amounts of data efficiently, even in scenarios with millions of documents, through optimized algorithms like FAISS.
Adaptability: Embeddings can be fine-tuned for specific domains, enhancing the accuracy of search results for particular use cases.
Scalability: Modern frameworks allow embedding search to scale horizontally, making it suitable for production environments handling large-scale queries.
Multilingual Capabilities: Embeddings can capture cross-lingual representations, enabling retrieval across different languages without requiring separate models.


```python
from sentence_transformers import SentenceTransformer


model_name, __ = "all-mpnet-base-v2", 768
model = SentenceTransformer(model_name)
model.encode("hello world").tolist()

search_query = {
    "knn": {
        "field": field,
        "query_vector": vector,
        "k": 5,
        "num_candidates": 10000,
    },
    "_source": [
        "title",
        "review_summary",
        "review_text",
        "description",
        "authors",
        "publisher",
        "categories",
        "review_score",
        "document_id",
    ]
}
```

_______________________________________________________________________________

## 6. Ingestion

The ingestion process in my project is divided into four containers:

1. The first container downloads the dataset and uploads it to MinIO.
2. The second container is MinIO, which stores the dataset in its raw form.
3. A third container runs a Python script to process the data.
4. The final container uploads the processed data to Elasticsearch.

This entire process is triggered when Docker Compose is executed, automating the data flow from download to processing and storage.


_______________________________________________________________________________



In summary, LLMs help create a personalized, intuitive, and efficient system for book recommendations, enhancing the reader’s experience by providing suggestions that are contextually relevant, insightful, and tailored to individual tastes.

____

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/jelambrar1)

Made with Love ❤️ by [@jelambrar96](https://github.com/jelambrar96)
