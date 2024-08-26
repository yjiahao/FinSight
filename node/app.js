import { ChatGroq } from "@langchain/groq";

// define the model
const llm = new ChatGroq(
    {
        model: "llama-3.1-8b-instant",
        temperature: 0.5,
    }
);

// create prompt template
const systemPrompt = `
You are a professional investor that follows the Warren Buffett philosophy of stock-picking.
The human is someone who is trying to pick up stock-investing.

Assist the human by providing detailed feedback about his investing ideas and help him with his stock analysis.
`

var humanPrompt = "How can I perform fundamental analysis?";

// call the prompt on the llm
const aiMsg = await llm.invoke(
    [
        [
            "system",
            systemPrompt,
        ],
        [
            "human",
            humanPrompt
        ],
    ]
);

// print out content of message
console.log(aiMsg.content);