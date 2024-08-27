import { ChatGroq } from "@langchain/groq";
import { ChatPromptTemplate } from "@langchain/core/prompts";

import { createStuffDocumentsChain } from "langchain/chains/combine_documents";
// import { createRetrievalChain } from "@langchain/core/retrieval";

import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";

import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { MemoryVectorStore } from "langchain/vectorstores/memory";

import * as dotenv from "dotenv";

import { HuggingFaceInferenceEmbeddings } from "@langchain/community/embeddings/hf";

// load dotnev
dotenv.config();

// define the LLm
const model = new ChatGroq(
    {
        model: "llama-3.1-8b-instant",
        temperature: 0.4,
    }
);

// create prompt template

// You are a professional investor that follows the Warren Buffett philosophy of stock-picking.
// The human is someone who is trying to pick up stock-investing.

// Assist the human by providing detailed feedback about his investing ideas and help him with his stock analysis.
const prompt = ChatPromptTemplate.fromTemplate(
    `
    Answer the question the human has based on the context: {context}
    Only use the context if you think it is relevant to the user's question. Otherwise, ignore it.

    Question: {input}
    `
);

// create chain
const chain = await createStuffDocumentsChain(
    {
        llm: model,
        prompt,
    }
);

// load data from webpage
const loader = new CheerioWebBaseLoader(
    "https://www.straitstimes.com/world/middle-east/major-israel-hezbollah-missile-exchange-as-region-fears-escalation"
  );

const docs = await loader.load();

// define the character splitter
const splitter = new RecursiveCharacterTextSplitter(
    {
        chunkSize: 200,
        chunkOverlap: 50
    }
);

// split documents with the document splitter
const splitDocs = await splitter.splitDocuments(docs);

// we only want to retrieve the most relevant documents, so we make use of a vector store
// create LLM to help us embed the splitted documents and queries
const embeddings = new HuggingFaceInferenceEmbeddings(
    'sentence-transformers/all-mpnet-base-v2'
);

const vectorStore = await MemoryVectorStore.fromDocuments(
    splitDocs,
    embeddings
);

// data retrieval
const retriever = vectorStore.asRetriever(
    {
        k: 10
    }
);

// https://js.langchain.com/v0.1/docs/use_cases/chatbots/retrieval/
const loadedDocs = await retriever.invoke("Summarize the events in the article");
console.log(loadedDocs);

// const response = await retrievalChain.invoke(
//     {
//         input: "What happened in the article?",
//     }
// );

// console.log(response);

// TODO: fix the splitting/loading of documents to ensure that we can capture most of the content
// read more on Cheerio to get the page content out (should be some method to do so i guess)