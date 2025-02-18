
from langchain.document_loaders import PyPDFLoader
import openai
from utilities import count_num_tokens


class Summarizer:

    @staticmethod
    def summarize_the_pdf(
        file_dir: str,
        max_final_token: int,
        token_threshold: int,
        gpt_model: str,
        temperature: float,
        summarizer_llm_system_role: str,
        final_summarizer_llm_system_role: str,
        character_overlap: int
    ):

        docs = []
        docs.extend(PyPDFLoader(file_dir).load())
        print(f"Document length: {len(docs)}")
        max_summarizer_output_token = int(
            max_final_token/len(docs)) - token_threshold
        full_summary = ""
        counter = 1
        print("Generating the summary..")
        # if the document has more than one pages
        if len(docs) > 1:
            for i in range(len(docs)):
                #Concatenation of docs content for prompt generation

                if i == 0:  # For the first page
                    prompt = docs[i].page_content + \
                        docs[i+1].page_content[:character_overlap]
                # For pages except the fist and the last one.
                elif i < len(docs)-1:
                    prompt = docs[i-1].page_content[-character_overlap:] + \
                        docs[i].page_content + \
                        docs[i+1].page_content[:character_overlap]
                else:  # For the last page
                    prompt = docs[i-1].page_content[-character_overlap:] + \
                        docs[i].page_content
                summarizer_llm_system_role = summarizer_llm_system_role.format(
                    max_summarizer_output_token)
                full_summary += Summarizer.get_llm_response(
                    gpt_model,
                    temperature,
                    summarizer_llm_system_role,
                    prompt=prompt
                )
        else:  # if the document has only one page
            full_summary = docs[0].page_content

            print(f"Page {counter} was summarized. ", end="")
            counter += 1
        print("\nFull summary token length:", count_num_tokens(
            full_summary, model=gpt_model))
        final_summary = Summarizer.get_llm_response(
            gpt_model,
            temperature,
            final_summarizer_llm_system_role,
            prompt=full_summary
        )
        return final_summary

    @staticmethod
    def get_llm_response(gpt_model: str, temperature: float, llm_system_role: str, prompt: str):

        response = openai.ChatCompletion.create(
            model="gpt-4",
            #engine=gpt_model,
            messages=[
                {"role": "system", "content": llm_system_role},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content
