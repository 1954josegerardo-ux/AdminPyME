# ============================================================================
#  LANZADOR DE ADMINPYME
#  Inicia el servidor Streamlit y abre el navegador automáticamente
# ============================================================================
import subprocess
import sys
import os
import time
import webbrowser
from threading import Timer

def obtener_ruta_base():
    """Obtiene la ruta donde está el ejecutable o el script."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def abrir_navegador():
    """Abre el navegador en la URL de Streamlit."""
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

def main():
    ruta_base = obtener_ruta_base()
    os.chdir(ruta_base)

    print("=" * 60)
    print("         📦 ADMINPYME - Sistema de Gestión")
    print("=" * 60)
    print()
    print("🚀 Iniciando el sistema...")
    print("🌐 El navegador se abrirá automáticamente.")
    print("⏹️  Para cerrar el sistema, cierra esta ventana.")
    print()

    # Abrir navegador después de 3 segundos
    Timer(3, abrir_navegador).start()

    # Iniciar Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Sistema cerrado. ¡Hasta pronto!")
    except Exception as e:
        print(f"❌ Error al iniciar: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()