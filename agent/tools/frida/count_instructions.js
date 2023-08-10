let instructionCount = 0;

// Função de callback para contar as instruções
function countInstructions() {
    instructionCount++;
}

// Faz o trace de todas as instruções
Interceptor.attach(ptr('0x0'), {
    onEnter: function(args) {
        countInstructions();
    }
});

// Encerra o trace após 15 segundos
setTimeout(function() {
    send(instructionCount);
}, 15000);