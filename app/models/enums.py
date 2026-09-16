import enum


class UserRole(str, enum.Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"


class OAuthProvider(str, enum.Enum):
    LINKEDIN = "linkedin"


class OrgMemberRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    RECRUITER = "recruiter"


class OrgCandidateStatus(str, enum.Enum):
    INVITED = "invited"
    ACTIVE = "active"
    HIRED = "hired"
    REJECTED = "rejected"


class CVStatus(str, enum.Enum):
    NONE = "none"
    PENDING = "pending"
    UPLOADED = "uploaded"


class ProfileSourceType(str, enum.Enum):
    CV = "cv"
    LINKEDIN = "linkedin"
    MANUAL = "manual"


class ProfileStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class QuizStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    PUBLISHED = "published"
    COMPLETED = "completed"
    EXPIRED = "expired"


class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FREE_TEXT = "free_text"
    TRUE_FALSE = "true_false"
    CODE = "code"


class SubmissionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    SCORED = "scored"
