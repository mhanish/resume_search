from pypdf import PdfReader
import os

# from pyresparser import ResumeParser
import re
import spacy

# import textacy
# from textacy import extract
from uuid import uuid4
from database import es, sync_es
from embedding_engine import get_embeddings

# Load the English model
nlp = spacy.load("en_core_web_md")

PDF_PATH = "./resumes"

RESUME_SECTIONS = [
    "Contact Information",
    "Objective",
    "Summary",
    "Education",
    "Experience",
    "Skills",
    "Projects",
    "Certifications",
    "Licenses",
    "Awards",
    "Honors",
    "Publications",
    "References",
    "Technical Skills",
    "Computer Skills",
    "Programming Languages",
    "Software Skills",
    "Soft Skills",
    "Language Skills",
    "Professional Skills",
    "Transferable Skills",
    "Work Experience",
    "Professional Experience",
    "Employment History",
    "Internship Experience",
    "Volunteer Experience",
    "Leadership Experience",
    "Research Experience",
    "Teaching Experience",
]


class ResumeParser:

    def __init__(self, resume: str, file_name) -> None:
        self.url = f"https://storage.cloud.google.com/mercor_dashboard_data/{file_name}"
        self.resume = resume
        self.clean = self.clean_text(resume)
        # self.text_doc = textacy.make_spacy_doc(self.clean, lang="en_core_web_md")
        self.doc = nlp(self.clean_text(resume))
        self.entities = self.extract_entities()
        self.name = self.extract_names()
        self.experience = self.extract_experience()
        self.emails = self.extract_emails()
        self.phones = self.extract_phone_numbers()
        self.years = self.extract_position_year()
        self.key_words = self.extract_particular_words()
        # self.key_terms = self.get_keyterms_based_on_sgrank()
        self.segments = self.segment_resume()

    def clean_text(self, text: str):
        # text = TextCleaner.remove_emails_links(text)
        doc = nlp(text)
        for token in doc:
            if token.pos_ == "PUNCT":
                text = text.replace(token.text, "")
        return str(text)

    def extract_names(self):
        names = [ent.text for ent in self.doc.ents if ent.label_ == "PERSON"]
        return names

    def extract_entities(self):
        entity_labels = ["GPE", "ORG"]
        entities = [
            token.text for token in self.doc.ents if token.label_ in entity_labels
        ]
        return list(set(entities))

    # def extract_experience(self):
    #     experience_section = []
    #     in_experience_section = False

    #     for token in self.doc:
    #         if token.text in RESUME_SECTIONS:
    #             if token.text == "Experience" or "EXPERIENCE" or "experience":
    #                 in_experience_section = True
    #             else:
    #                 in_experience_section = False

    #         if in_experience_section:
    #             experience_section.append(token.text)

    #     return " ".join(experience_section)

    def extract_emails(self):
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        emails = re.findall(email_pattern, self.resume)
        return emails

    def extract_phone_numbers(self):
        phone_number_pattern = (
            r"^(\+\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$"
        )
        phone_numbers = re.findall(phone_number_pattern, self.resume)
        return phone_numbers

    def extract_position_year(self):
        position_year_search_pattern = (
            r"(\b\w+\b\s+\b\w+\b),\s+(\d{4})\s*-\s*(\d{4}|\bpresent\b)"
        )
        position_year = re.findall(position_year_search_pattern, self.resume)
        return position_year

    def extract_particular_words(self):
        pos_tags = ["NOUN", "PROPN"]
        nouns = [token.text for token in self.doc if token.pos_ in pos_tags]
        return nouns

    def segment_resume(self):
        segments = {
            "personal_details": "",
            "education": "",
            "experience": "",
            "skills": "",
            "certifications": "",
        }

        patterns = {
            "education": re.compile(r"(education|qualifications)", re.IGNORECASE),
            "experience": re.compile(
                r"(experience|employment|work history)", re.IGNORECASE
            ),
            "skills": re.compile(r"(skills|technical skills)", re.IGNORECASE),
            "certifications": re.compile(
                r"(certifications|certificates)", re.IGNORECASE
            ),
        }

        current_section = "personal_details"
        for line in self.resume.split("\n"):
            line = line.strip()
            if not line:
                continue
            for section, pattern in patterns.items():
                if pattern.search(line):
                    current_section = section
                    break
            segments[current_section] += line + "\n"

        return segments

    def get_json(self):
        resume_dictionary = {
            "unique_id": str(uuid4()),
            "url": self.url,
            "resume_data": self.resume,
            # "clean_data": self.clean_data,
            "entities": self.entities,
            "extracted_keywords": self.key_words,
            # "keyterms": self.key_terms,
            "name": self.name,
            "experience": self.experience,
            "emails": self.emails,
            "phones": self.phones,
            "years": self.years,
            "segments": self.segments,
            # "bi_grams": str(self.bi_grams),
            # "tri_grams": str(self.tri_grams),
            # "pos_frequencies": self.pos_frequencies,
        }

        return resume_dictionary

    # def get_keyterms_based_on_sgrank(self):
    #
    #     return list(
    #         extract.keyterms.sgrank(
    #             self.text_doc, normalize="lemma", topn=20
    #         )
    #     )


def read_single_pdf(file_path: str) -> str:
    output = []
    try:
        with open(file_path, "rb") as f:
            pdf_reader = PdfReader(f)
            count = len(pdf_reader.pages)
            for i in range(count):
                page = pdf_reader.pages[i]
                output.append(page.extract_text())
    except Exception as e:
        print(f"Error reading file '{file_path}': {str(e)}")
    return str(" ".join(output))


# def extract_metadata(file_path: str):
#     data = ResumeParser(file_path).get_extracted_data()
#     return data
# print(extract_metadata("./resumes/2020mcb1228@iitrpr.ac.in_resume.pdf"))

# print(ResumeParser(read_single_pdf("./resumes/2020mcb1228@iitrpr.ac.in_resume.pdf")).get_json()["segments"])


def parse_resume(file_path, file_name):
    print("parsing resume")
    resume_json = ResumeParser(read_single_pdf(file_path), file_name).get_json()
    segments = []
    for key, value in resume_json["segments"].items():
        try:
            embeddings_response = get_embeddings(input_list=[value])
            if not len(embeddings_response.json()["outputs"]):
                raise Exception
        except Exception as e:
            print("ML server communication could not be established.", e)

        segment = {
            "segment": key,
            "content": value,
            "embedding": embeddings_response.json()["outputs"][0],
        }
        segments.append(segment)

    resume_json["segments"] = segments
    return resume_json
    #     raise QueryError("1")


def index_single_document(body):

    # Index the document
    print("Indexing Document")
    response = sync_es.index(index="resumes", body=body)
    print(response)


# Read through PDFs from the folder and index them
# for file_name in os.listdir("./resumes"):
#     if file_name.endswith(".pdf"):
#         file_path = os.path.join("./resumes", file_name)
#         content = parse_resume(file_path, file_name)
#         response = index_single_document(content)
#         print(f"Indexed {file_name}: {response}")


# Search
def search_query(query):
    try:
        embeddings_response = get_embeddings(input_list=[query])
        if not len(embeddings_response.json()["outputs"]):
            raise Exception
    except Exception as e:
        print("ML server communication could not be established.", e)
    query_vector = embeddings_response.json()["outputs"][0]
    # print(query_vector)
    search_query = {
        "knn": {
            "field": "segments.embedding",
            "query_vector": query_vector,
            "k": 100,
            "num_candidates": 1000,
            "inner_hits": {
                "size": 100,
                "_source": False,
                "fields": ["segments.content"],
            },
        }
    }
    result = []

    response = sync_es.search(index="resumes", body=search_query)
    # print(response)
    for hit in response.get("hits").get("hits"):
        res_dict = {}
        doc_id = hit["_id"]
        inner_hits = hit["inner_hits"]["segments"]["hits"]["hits"]
        res_dict["url"] = hit.get("_source").get("url")
        res_dict["fields"] = inner_hits
        result.append(res_dict)
    return result


def expand_query(query):
    # Example expansion using synonyms
    expansions = {
        "python developer": ["python programmer", "python engineer"],
        "aws": ["Amazon Web Services"],
        "computer vision": ["image processing", "visual recognition"],
        "stem": ["Science", "Maths", "Engineering", "Technology"],
        "iit": ["Indian Institute of Technology"],
        "big tech": ["Google", "Meta", "Amazon"],
    }

    # expanded_queries = [query]
    for term, synonyms in expansions.items():
        if term in query.lower():
            query = str(query.lower()).replace(term, term + ", " + ", ".join(synonyms))
    print(query)
    return query


# search_query("Person with experience in PHP")
