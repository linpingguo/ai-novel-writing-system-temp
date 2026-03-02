from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Float, JSONB, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    subscription_tier = Column(String(20), default='free')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    genre = Column(String(50), nullable=False)
    target_word_count = Column(Integer, default=80000)
    current_word_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Character(Base):
    __tablename__ = "characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    personality = Column(JSONB)
    appearance = Column(Text)
    background = Column(Text)
    traits = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CharacterRelation(Base):
    __tablename__ = "character_relations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_char_id = Column(UUID(as_uuid=True), ForeignKey('characters.id'), nullable=False)
    target_char_id = Column(UUID(as_uuid=True), ForeignKey('characters.id'), nullable=False)
    relation_type = Column(String(20), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('source_char_id', 'target_char_id', name='unique_character_pair'),
    )


class OutlineNode(Base):
    __tablename__ = "outline_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('outline_nodes.id'), nullable=True, index=True)
    node_type = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    order_num = Column(Integer, nullable=False)
    word_count_estimate = Column(Integer, default=0)
    involved_characters = Column(JSONB)
    viral_node_id = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False, index=True)
    outline_node_id = Column(UUID(as_uuid=True), ForeignKey('outline_nodes.id'), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    content_format = Column(String(20), default='markdown')
    word_count = Column(Integer, default=0)
    status = Column(String(20), default='draft')
    ai_generated_ratio = Column(Float, default=0)
    style_score = Column(Float)
    ai_flavor_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class StyleBaseline(Base):
    __tablename__ = "style_baselines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False, index=True)
    sentence_patterns = Column(JSONB)
    vocabulary_profile = Column(JSONB)
    tone_markers = Column(JSONB)
    perspective = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ViralStructureTemplate(Base):
    __tablename__ = "viral_structure_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    genre = Column(String(50), nullable=False)
    description = Column(Text)
    key_nodes = Column(JSONB, nullable=False)
    success_cases = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ProjectViralStructure(Base):
    __tablename__ = "project_viral_structures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False, unique=True, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey('viral_structure_templates.id'), nullable=False)
    custom_nodes = Column(JSONB)
    current_node = Column(String(100))
    completion_score = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
