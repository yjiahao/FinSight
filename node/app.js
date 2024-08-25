import { ChatGroq } from "@langchain/groq";

const llm = new ChatGroq({
    model: "llama-3.1-8b-instant",
    temperature: 0,
  });

const prompt = `
You are a professional investor that follows the Warren Buffett philosophy of stock-picking.
The human is someone who is trying to pick up stock-investing.

Assist the human by providing detailed feedback about his investing ideas and help him with his stock analysis.
`

const aiMsg = await llm.invoke(
    [
        [
            "system",
            prompt,
        ],
        [
            "human",
            "How can I perform fundamental analysis?"
        ],
    ]
);

// print out content of message
console.log(aiMsg.content);