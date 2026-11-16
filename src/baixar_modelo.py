
"""Baixa os arquivos do modelo sem carregá-lo na memória RAM."""

from pathlib import Path
from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[1]

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

MODEL_DIR = ROOT / "models" / "qwen2.5-1.5b-instruct"


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Baixando {MODEL_ID}...")
    print(f"Destino: {MODEL_DIR}")

    snapshot_download(
        repo_id=MODEL_ID,
        local_dir=str(MODEL_DIR)
    )

    print("\nDownload concluído!")
    print("Os arquivos estão armazenados localmente.")
    print("O modelo poderá ser carregado posteriormente offline.")


if __name__ == "__main__":
    main()

