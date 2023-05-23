import openai
from transformers import AutoTokenizer, RobertaForMaskedLM
import torch

class RobertaPostprocessor:
    def __init__(self, debug=False):
        self.tokenizer = AutoTokenizer.from_pretrained("roberta-base")
        self.model = RobertaForMaskedLM.from_pretrained("roberta-base")
        if torch.cuda.is_available():
            self.model = self.model.cuda()
    
    def __call__(self, text):
        if isinstance(text, str):
            input_text = [text]
        else:
            input_text = text
        inputs = self.tokenizer(input_text, return_tensors="pt", padding=True)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        with torch.no_grad():
            logits = self.model(**inputs).logits
        out = self.tokenizer.batch_decode(logits.argmax(dim=2))
        out = [out.replace('<s>', '').replace('</s>', '').strip() for out in out]
        if isinstance(text, str):
            return out[0]
        return out

def postprocess(text):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a masterful text postprocessor."},
            {"role": "user", "content": "I need you to simulate a text postprocessor. When I write postprocess('texttisbetter') you respond with a 'text is better' replacing the input to postprocess with the most plausible text. No explanations, no small talk, no questions, no excuses, only the result. If the input is too hard, just return the input. postprocess('BECOMINGMORE')"},
            {"role": "assistant", "content": "BECOMING MORE"},
            {"role": "user", "content": "postprocess('%s')"%text}
        ]
    )
    return response["choices"][0]["message"]["content"]