from DocDeti_Bot import app as application

if __name__ == "__main__":
    # Этот блок нужен только для локального тестирования
    from threading import Thread
    from DocDeti_Bot import bot
    
    Thread(target=lambda: application.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )).start()
    
    bot.run()
