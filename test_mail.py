# test_mail.py  ← en la raíz del proyecto
import asyncio
from fastapi_mail import FastMail, MessageSchema, MessageType
from app.config.mail_config import conf

async def enviar_prueba():
    fm = FastMail(conf)
    
    message = MessageSchema(
        subject="Prueba exitosa - Hospital Tecpán",
        recipients=["ticshosptecpan@gmail.com"],   # CAMBIA ESTO por tu correo real
        body="""
        <h2>¡El sistema de correos funciona perfectamente!</h2>
        <p>Este es un mensaje de prueba enviado desde tu backend FastAPI.</p>
        <p>Todo está listo para enviar correos de registro, recuperación de contraseña, etc.</p>
        <br>
        <p><strong>¡Ya puedes seguir con el resto del proyecto!</strong></p>
        """,
        subtype=MessageType.html
    )
    
    await fm.send_message(message)
    print("CORREO ENVIADO CON ÉXITO")

# Ejecutar
asyncio.run(enviar_prueba())