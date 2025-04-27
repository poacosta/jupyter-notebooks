import {agent, QueryEngineTool, VectorStoreIndex, StopEvent} from "llamaindex";
import {ChromaVectorStore} from '@llamaindex/chroma';
import {openai} from "@llamaindex/openai";
import * as dotenv from "dotenv";

dotenv.config();

async function initialize() {
  const vectorStore = new ChromaVectorStore({
    collectionName: "base_knowledge",
    chromaClientParams: {
      path: "http://ip-address:8000"
    },
    textKey: "documents"
  });

  const index = await VectorStoreIndex.fromVectorStore(vectorStore);
  const queryEngine = index.asQueryEngine();

  const queryEngineTool = new QueryEngineTool({
    queryEngine,
    toolName: "search people",
    description: "search for people name and descriptions in the database",
    returnDirect: true,
  });

  const bookAgent = agent({
    name: "people",
    description: "descriptions for various types of people",
    tools: [queryEngineTool],
    llm: openai({
      model: "o3-mini",
      apiKey: process.env.OPENAI_API_KEY,
      temperature: 0.1,
    })
  });

  return {bookAgent};
}

async function runQuery(queryText: string): Promise<StopEvent<string>> {
  try {
    const {bookAgent} = await initialize();
    return await bookAgent.run(queryText);
  } catch (error) {
    console.error("Query error:", error);
    throw error;
  }
}

async function main() {
  const result = await runQuery("Search the database for people name and descriptions.");
  console.log(result);
}

if (require.main === module) {
  main();
}

export {runQuery};
