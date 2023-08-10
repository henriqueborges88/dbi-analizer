// Nome da função da API do Windows que queremos instrumentar
var targetFunction = 'MessageBoxW';

// Importar as funções necessárias para a instrumentação
var user32 = Module.findBaseAddress('user32.dll');
var MessageBoxW = new NativeFunction(Module.findExportByName(user32, targetFunction), 'int', ['pointer', 'pointer', 'pointer', 'int']);

// Substituir a função original por nossa implementação personalizada
Interceptor.replace(MessageBoxW, new NativeCallback(function (hwnd, text, caption, type) {
    console.log('MessageBoxW foi chamado:');
    console.log('   Texto: ' + text.readUtf16String());
    console.log('   Título: ' + caption.readUtf16String());
    return 0; // Simula o retorno de sucesso da MessageBoxW
}, 'int', ['pointer', 'pointer', 'pointer', 'int']));