"""Configuración central del equipo editorial.

Toda la parametrización (modelos, credenciales, política editorial) se lee de
variables de entorno / archivo `.env` mediante `pydantic-settings`. Esto mantiene
los secretos fuera del código y permite cambiar de comportamiento sin tocar el
código fuente — una de las "mejores prácticas" del tutorial.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Claude / Anthropic ---
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    # --- Modelos por agente ---
    model_scout: str = Field(default="claude-opus-4-8", alias="MODEL_SCOUT")
    model_curator: str = Field(default="claude-sonnet-4-6", alias="MODEL_CURATOR")
    model_fact_checker: str = Field(default="claude-opus-4-8", alias="MODEL_FACT_CHECKER")
    model_writer: str = Field(default="claude-opus-4-8", alias="MODEL_WRITER")
    model_critic: str = Field(default="claude-opus-4-8", alias="MODEL_CRITIC")
    model_illustrator: str = Field(default="claude-sonnet-4-6", alias="MODEL_ILLUSTRATOR")
    model_social: str = Field(default="claude-sonnet-4-6", alias="MODEL_SOCIAL")

    # --- Línea editorial ---
    region_focus: str = Field(default="Argentina y Latinoamérica", alias="REGION_FOCUS")
    languages: str = Field(default="es", alias="LANGUAGES")
    num_topics: int = Field(default=4, alias="NUM_TOPICS")
    max_revisions: int = Field(default=2, alias="MAX_REVISIONS")
    min_sources_per_claim: int = Field(default=2, alias="MIN_SOURCES_PER_CLAIM")
    blog_name: str = Field(default="Real Estate Insights", alias="BLOG_NAME")

    # --- Imágenes ---
    image_provider: str = Field(default="none", alias="IMAGE_PROVIDER")  # openai | none
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    image_size: str = Field(default="1536x1024", alias="IMAGE_SIZE")

    # --- Blog (WordPress) ---
    wordpress_url: str = Field(default="", alias="WORDPRESS_URL")
    wordpress_user: str = Field(default="", alias="WORDPRESS_USER")
    wordpress_app_password: str = Field(default="", alias="WORDPRESS_APP_PASSWORD")
    wordpress_status: str = Field(default="draft", alias="WORDPRESS_STATUS")

    # --- Redes sociales (upload-post.com) ---
    uploadpost_api_key: str = Field(default="", alias="UPLOADPOST_API_KEY")
    uploadpost_user: str = Field(default="", alias="UPLOADPOST_USER")
    social_platforms: str = Field(
        default="instagram,linkedin,facebook,x", alias="SOCIAL_PLATFORMS"
    )

    # --- Ejecución ---
    dry_run: bool = Field(default=True, alias="DRY_RUN")
    output_dir: str = Field(default="output", alias="OUTPUT_DIR")

    @property
    def social_platform_list(self) -> list[str]:
        return [p.strip() for p in self.social_platforms.split(",") if p.strip()]


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia única (cacheada) de la configuración."""
    return Settings()
