# LLM-Prompt-Evaluation-and-Engineering
LLM Prompt Evaluation and Engineering for summarization and Named Entity Recognition Capability

Training an LLM involves 2 main stages:
1) Pre-training
2) Instruction Tuning

My goal was to make a novel instruction tuning framework for training the LLMs. After the LLM is trained it is necessary to evaluate the LLM on different prompts using the appropriate evaluation metrics. 
Instruction tuning refers to the process of optimizing or fine-tuning the instructions or commands given to a computer or a specific software program to achieve better performance or efficiency. In our case we need to make sure the instructions/prompts are good enough for the LLMs to be trained on. So the goal is to convert the entire data in the form of instruction but what type of instructions should one make and will these instructions help in reducing the hallucinations in the LLM which is trained on these instructions? 

Challenge: There is almost no past literature which dives into the instruction tuning mechanism of training LLMs. 

Solution: In an effort to develop a good prompt/instruction engineering framework I decided to use the organized prompt development methodology which is something I created myself. I categorised my prompt developments to various categories and evaluated the prompts I created on open source LLMs. Based on the performance on these open source LLM's, I decided whether to include such intructions/prompts to my instruction tuning dataset. I also made sure to mitigate hallucination by making hallucination specific prompts. 

Result: In the end, the LLM which was trained was able to perform well on the instructions where other open source LLMs failed. Because we had an evaluation pipeline inside the prompt development framework, we were also able to use the same code to evaluate the final LLM, thus resulting in reducing of evaluation time by over 60%. Because one could use this same framework to evaluate LLMs and the prompts without a human in the loop. 

There is an internship report and a presentation available in this repository. I would be happy to present it to you and explain this groundbreaking work in more detail. 
