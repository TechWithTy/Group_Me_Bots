from nicegui import ui

def build():
    ui.label('Hello World')

ui.run(build, port=8082)
input('Press Enter to stop...')
