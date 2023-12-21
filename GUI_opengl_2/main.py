from GUI import GUI

from os import system
system('gcc -shared -o opengl_drawer.dll opengl_drawer.c -lopengl32 -lgdi32')


if __name__ == '__main__':
	GUI()