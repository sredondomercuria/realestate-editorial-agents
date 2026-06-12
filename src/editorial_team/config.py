"""Configuración central del equipo editorial.

Toda la parametrización (modelos, credenciales, política editorial, infraestructura)
se lee de variables de entorno / archivo `.env` mediante `pydantic-settings`. Esto
mantiene los secretos fuera del código y permite cambiar de comportamiento sin tocar
el código fuente.

Infra: el proyecto corre 100% local (SQLite + .env), pero está preparado para GCP
(Cloud Run + Secret Manager + Cloud Scheduler). Ver `editorial_team.gcp_secrets` y
`docs/10-deploy-gcp.md`.
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

    # --- Runtime de los agentes ---
    # hybrid -> la producción editorial (investigar+validar+redactar+revisar) corre
    #           como un Managed Agent en la plataforma de Claude; el resto en LangGraph.
    # local  -> todo el pipeline corre como nodos LangGraph en este backend.
    agent_runtime: str = Field(default="hybrid", alias="AGENT_RUNTIME")
    # IDs cacheados del Managed Agent (se crean una vez; ver editorial_team.integrations.managed_agents)
    managed_agent_id: str = Field(default="", alias="MANAGED_AGENT_ID")
    managed_env_id: str = Field(default="", alias="MANAGED_ENV_ID")

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

    # --- Investigación / búsqueda ---
    # claude  -> herramientas server-side web_search + web_fetch
    # tavily  -> API Tavily (optimizada para agentes) + síntesis con Claude
    research_backend: str = Field(default="claude", alias="RESEARCH_BACKEND")
    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")

    # --- Generación de imágenes ---
    # IMAGE_PROVIDER:
    #   gemini -> API de AI Studio (key GEMINI_API_KEY, crédito prepago)
    #   vertex -> Vertex AI en tu proyecto GCP (factura por GCP; en Cloud Run sin key)
    #   openai -> gpt-image-1
    #   none   -> no genera
    image_provider: str = Field(default="gemini", alias="IMAGE_PROVIDER")
    # Modelos: Gemini "Nano Banana" (gemini-3-pro-image / gemini-3.1-flash-image /
    #   gemini-2.5-flash-image) o, en Vertex, Imagen (imagen-4.0-generate-001 / -fast-).
    image_model: str = Field(default="gemini-3-pro-image", alias="IMAGE_MODEL")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    image_size: str = Field(default="1536x1024", alias="IMAGE_SIZE")
    # Vertex AI (cuando IMAGE_PROVIDER=vertex). Usa GCP_PROJECT (definido abajo).
    vertex_location: str = Field(default="global", alias="VERTEX_LOCATION")

    # --- Hosting de imágenes (CDN) ---
    # IMAGE_HOST: cloudinary | none
    image_host: str = Field(default="none", alias="IMAGE_HOST")
    cloudinary_url: str = Field(default="", alias="CLOUDINARY_URL")

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

    # --- Persistencia ---
    database_path: str = Field(default="output/editorial.db", alias="DATABASE_PATH")

    # --- Webapp / UI ---
    web_host: str = Field(default="0.0.0.0", alias="WEB_HOST")
    web_port: int = Field(default=8080, alias="PORT")  # Cloud Run inyecta PORT
    scheduler_token: str = Field(default="", alias="SCHEDULER_TOKEN")

    # --- GCP ---
    use_gcp_secrets: bool = Field(default=False, alias="USE_GCP_SECRETS")
    gcp_project: str = Field(default="", alias="GCP_PROJECT")

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
