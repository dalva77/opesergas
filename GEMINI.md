# INSTRUCCIONES PARA GEMINI CODE ASSIST Y CLI

- Nunca utilices el comando **ReadManyFiles**. Si quieres leer multiples ficheros, utiliza **ReadFile** con cada fichero, llamandolos con su path completo
- Habla SIEMPRE en español. Utiliza ingles para los nombres de funciones, variables, clases etc. del codigo que escribas
- NUNCA ADULES AL USUARIO. Valora sus propuestas de forma constructiva pero critica
- Al inicio de la sesion, lee el contenido del fichero README.md para empezar a orientarte en el proyecto, y sigue sus instrucciones
- Al generar codigo python, procura seguir las convenciones de Flake8 y procura que las lineas no excedan de 120 caracteres
- Considera refactorizar el codigo cuando los ficheros excedan aproximadamente 300 lineas
- Propon siempre un desarrollo dirigido por tests (TDD). Primero se deciden los casos a testar, luego se escriben los tests y finalmente el codigo que satisfaga todos los tests
- Al finalizar la sesion, actualiza el contenido de toda la documentacion del proyecto, empezando por guardar un resumen del contexto de la sesion en AI_CONTEXT.md. Continua con el resto de ficheros de documentacion descritos en README.md
