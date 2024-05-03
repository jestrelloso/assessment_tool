from db.database import Base
from .choices_model import Choice
from .question_model import Question
from .exam_model import Exam
from .user_model import User
from .examinee_exam_table_model import examinee_exam_table
from .admin_model import Admin
from .examiner_model import Examiner
from .request_exam_model import RequestExam

metadata = Base.metadata
