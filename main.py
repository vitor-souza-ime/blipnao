import qi
import torch
from PIL import Image
import numpy as np
import time
import os
from datetime import datetime
from transformers import BlipProcessor, BlipForConditionalGeneration
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def setup_output_directory():
    """Cria diretório para salvar as imagens"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"nao_captures_{timestamp}"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✓ Diretório criado: {output_dir}")
    
    return output_dir

def save_image(image, output_dir, iteration, caption=""):
    """Salva a imagem com timestamp e legenda"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"nao_image_{iteration:04d}_{timestamp}.jpg"
    filepath = os.path.join(output_dir, filename)
    
    # Salvar a imagem
    image.save(filepath, quality=95)
    
    # Criar arquivo de texto com a legenda
    if caption:
        txt_filename = f"nao_image_{iteration:04d}_{timestamp}.txt"
        txt_filepath = os.path.join(output_dir, txt_filename)
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Caption: {caption}\n")
    
    print(f"✓ Imagem salva: {filepath}")
    return filepath

def display_image(image, caption="", iteration=1):
    """Exibe a imagem em uma janela usando matplotlib"""
    plt.figure(figsize=(10, 8))
    
    # Exibir a imagem
    plt.subplot(2, 1, 1)
    plt.imshow(image)
    plt.axis('off')
    plt.title(f"NAO Camera - Iteration {iteration}", fontsize=14, fontweight='bold')
    
    # Exibir a legenda
    plt.subplot(2, 1, 2)
    plt.text(0.5, 0.5, f"Caption: {caption}", 
             horizontalalignment='center', verticalalignment='center',
             fontsize=12, wrap=True, transform=plt.gca().transAxes,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
    plt.axis('off')
    
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)  # Permite que a janela seja atualizada
    
    return plt.gcf()

def setup_live_display():
    """Configura display em tempo real usando matplotlib"""
    plt.ion()  # Ativar modo interativo
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Configurar subplot da imagem
    ax1.set_title("NAO Camera Feed", fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    # Configurar subplot da legenda
    ax2.axis('off')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    
    return fig, ax1, ax2

def update_live_display(fig, ax1, ax2, image, caption, iteration):
    """Atualiza o display em tempo real"""
    # Limpar axes
    ax1.clear()
    ax2.clear()
    
    # Atualizar imagem
    ax1.imshow(image)
    ax1.axis('off')
    ax1.set_title(f"NAO Camera - Iteration {iteration} - {datetime.now().strftime('%H:%M:%S')}", 
                  fontsize=14, fontweight='bold')
    
    # Atualizar legenda
    ax2.text(0.5, 0.5, f"Caption: {caption}", 
             horizontalalignment='center', verticalalignment='center',
             fontsize=12, wrap=True, transform=ax2.transAxes,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"))
    ax2.axis('off')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    
    # Atualizar display
    plt.tight_layout()
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.1)

def connect_to_nao(ip="172.15.1.29", port=9559):
    """Conecta ao robô NAO"""
    session = qi.Session()
    session.connect(f"tcp://{ip}:{port}")
    return session

def capture_image_from_nao(session):
    """Captura uma imagem da câmera do NAO"""
    try:
        # Método 1: Tentar usando ALVideoDevice com subscribeCamera
        camera_service = session.service("ALVideoDevice")
        
        # Configurações da câmera
        camera_id = 0  # Câmera superior
        resolution = 2  # VGA (640x480)
        color_space = 11  # RGB
        fps = 5  # Reduzir FPS para evitar problemas
        
        # Tentar diferentes métodos de subscrição
        try:
            # Método mais comum no NAOqi 2.x
            video_client = camera_service.subscribeCamera("python_client", camera_id, resolution, color_space, fps)
        except AttributeError:
            try:
                # Método alternativo
                video_client = camera_service.subscribe("python_client", resolution, color_space, fps)
            except AttributeError:
                # Último método alternativo
                video_client = "python_client"
                camera_service.setActiveCamera(camera_id)
                camera_service.setResolution(video_client, resolution)
                camera_service.setColorSpace(video_client, color_space)
                camera_service.setFrameRate(video_client, fps)
        
        # Pequena pausa para estabilizar
        time.sleep(0.1)
        
        # Capturar imagem
        nao_image = camera_service.getImageRemote(video_client)
        
        # Verificar se a imagem foi capturada corretamente
        if nao_image is None or len(nao_image) < 7:
            raise Exception("Falha ao capturar imagem da câmera")
        
        # Extrair dados da imagem
        width = nao_image[0]
        height = nao_image[1]
        channels = nao_image[2]
        image_data = nao_image[6]
        
        print(f"Imagem capturada: {width}x{height}, {channels} canais")
        
        # Converter para numpy array
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        image_array = image_array.reshape((height, width, channels))
        
        # Converter para PIL Image (RGB)
        image = Image.fromarray(image_array).convert("RGB")
        
        return image
        
    except Exception as e:
        print(f"Erro na captura da imagem: {e}")
        # Tentar método alternativo usando ALPhotoCapture
        return capture_image_alternative(session)
    
    finally:
        # Limpar subscrição se possível
        try:
            if 'video_client' in locals() and hasattr(camera_service, 'unsubscribe'):
                camera_service.unsubscribe(video_client)
        except:
            pass

def capture_image_alternative(session):
    """Método alternativo usando ALPhotoCapture"""
    try:
        print("Tentando método alternativo com ALPhotoCapture...")
        photo_service = session.service("ALPhotoCapture")
        
        # Configurar parâmetros
        photo_service.setResolution(2)  # VGA
        photo_service.setPictureFormat("jpg")
        
        # Tirar foto e salvar temporariamente
        temp_path = "/tmp/nao_temp_image.jpg"
        photo_service.takePicture(temp_path)
        
        # Carregar a imagem
        image = Image.open(temp_path)
        
        return image
        
    except Exception as e:
        print(f"Erro no método alternativo: {e}")
        # Se tudo falhar, criar uma imagem de teste
        print("Criando imagem de teste...")
        return Image.new('RGB', (640, 480), color='blue')

def get_camera_info(session):
    """Obtém informações sobre as câmeras disponíveis"""
    try:
        camera_service = session.service("ALVideoDevice")
        
        # Listar métodos disponíveis
        print("Métodos disponíveis no ALVideoDevice:")
        for method in dir(camera_service):
            if not method.startswith('_'):
                print(f"  - {method}")
        
        # Verificar câmeras disponíveis
        if hasattr(camera_service, 'getCameraIndexes'):
            cameras = camera_service.getCameraIndexes()
            print(f"Câmeras disponíveis: {cameras}")
        
        return camera_service
        
    except Exception as e:
        print(f"Erro ao obter informações da câmera: {e}")
        return None

def speak_text(session, text):
    """Faz o robô falar o texto"""
    try:
        tts_service = session.service("ALTextToSpeech")
        
        # Verificar idiomas disponíveis
        if hasattr(tts_service, 'getAvailableLanguages'):
            languages = tts_service.getAvailableLanguages()
            print(f"Idiomas disponíveis: {languages}")
        
        # Configurar idioma (tentar inglês primeiro)
        try:
            tts_service.setLanguage("English")
        except:
            try:
                tts_service.setLanguage("en-US")
            except:
                print("Usando idioma padrão")
        
        tts_service.setVolume(0.7)
        tts_service.say(text)
        
    except Exception as e:
        print(f"Erro na síntese de voz: {e}")

def main():
    print("=== Sistema de Visão NAO com BLIP ===")
    
    # Setup do diretório de saída
    print("Configurando diretório de saída...")
    output_dir = setup_output_directory()
    
    # Passo 1: Conectar ao NAO
    print("Conectando ao NAO...")
    try:
        session = connect_to_nao("172.15.1.29", 9559)
        print("✓ Conectado com sucesso!")
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")
        return
    
    # Verificar informações da câmera
    print("\nVerificando câmeras disponíveis...")
    camera_service = get_camera_info(session)
    
    # Passo 2: Carregar o modelo BLIP
    print("\nCarregando modelo BLIP...")
    try:
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
        print("✓ Modelo BLIP carregado!")
    except Exception as e:
        print(f"✗ Erro ao carregar modelo: {e}")
        return
    
    # Setup do display em tempo real
    print("\nConfigurando display em tempo real...")
    fig, ax1, ax2 = setup_live_display()
    
    # Loop principal
    print("\n=== Iniciando captura e geração de legendas ===")
    print("Pressione Ctrl+C para parar")
    print(f"Imagens serão salvas em: {output_dir}\n")
    
    iteration = 1
    try:
        while True:
            print(f"--- Iteração {iteration} ---")
            
            # Passo 3: Capturar imagem
            print("📸 Capturando imagem...")
            try:
                image = capture_image_from_nao(session)
                print("✓ Imagem capturada!")
            except Exception as e:
                print(f"✗ Erro na captura: {e}")
                time.sleep(5)
                iteration += 1
                continue
            
            # Passo 4: Processar com BLIP
            print("🤖 Processando com BLIP...")
            try:
                inputs = processor(images=image, return_tensors="pt")
                
                # Gerar legenda
                with torch.no_grad():
                    output = model.generate(**inputs, max_length=50)
                    caption = processor.decode(output[0], skip_special_tokens=True)
                
                print(f"✓ Legenda: '{caption}'")
                
            except Exception as e:
                print(f"✗ Erro no processamento BLIP: {e}")
                caption = "Erro no processamento"
            
            # Passo 5: Salvar imagem
            print("💾 Salvando imagem...")
            try:
                filepath = save_image(image, output_dir, iteration, caption)
            except Exception as e:
                print(f"✗ Erro ao salvar imagem: {e}")
            
            # Passo 6: Exibir imagem
            print("🖼️  Exibindo imagem...")
            try:
                update_live_display(fig, ax1, ax2, image, caption, iteration)
                print("✓ Imagem exibida!")
            except Exception as e:
                print(f"✗ Erro ao exibir imagem: {e}")
            
            # Passo 7: Falar a legenda
            print("🔊 NAO falando...")
            try:
                speak_text(session, caption)
                print("✓ Fala concluída!")
            except Exception as e:
                print(f"✗ Erro na fala: {e}")
            
            # Aguardar próxima iteração
            print("⏱️  Aguardando 5 segundos...\n")
            time.sleep(5)
            iteration += 1
            
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}")
    finally:
        plt.close('all')  # Fechar todas as janelas matplotlib
    
    print(f"Programa finalizado! Imagens salvas em: {output_dir}")

if __name__ == "__main__":
    main()
