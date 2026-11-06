import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) == "scripts":
  root_dir = os.path.abspath(os.path.join(current_dir, ".."))
else:
  root_dir = current_dir

backend_dir = os.path.join(root_dir, "backend")
sys.path.insert(0, backend_dir)

print(f"Diretório backend detetado: {backend_dir}")
print("A testar os caminhos de importação...")

try:
  print("1. A tentar importar a Base do SQLAlchemy...")
  from app.core.database import Base
  print("   -> Sucesso! Base encontrada em app.core.database.")

  print("2. A tentar importar o QueryLogModel...")
  from app.modules.chat.models import QueryLogModel
  print("   -> Sucesso! QueryLogModel encontrado.")

  print("\nTudo validado com sucesso!")
except Exception as e:
  print(f"\n[ERRO DE IMPORTAÇÃO]: {e}")