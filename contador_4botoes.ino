#include <Adafruit_GFX.h>
#include <MCUFRIEND_kbv.h>
#include <GFButton.h>
#include <EEPROM.h>


MCUFRIEND_kbv tela;
int qtd[4] = {0, 99, 999, 1000};
String contagem = "Setor";
int altura = 50;
unsigned long instanteAnteriorDeDeteccao = 0;
bool posicaoAnterior; 
bool posicao;
unsigned long temposPressionados[4] = {0, 0, 0, 0};
int space[4] = {0, 0, 0, 0};
String unidades[4] = {"g", "M", "L", "mm"};

int enderecoQtd = 0; //8 bytes -> de 0 a 7
int enderecoContagem = enderecoQtd + 8; // 1 + 20 (max de caracteres) ->8 a 28
int enderecoUnidades = enderecoContagem + 21; //4 unidades de ate 5 letras = 24 bytes -> 29 a 52

GFButton btn1(A8);
GFButton btn2(A9);
GFButton btn3(A10);
GFButton btn4(A11);

void setup() {

  Serial.begin(9600);
  carregarDadosDaEEPROM();
  // esperarDadosSerial();

  tela.begin(tela.readID());
  tela.fillScreen(TFT_BLACK);

  mostrarPrimeiraColuna();
   
  mostrarSegundaColuna();

  btn1.setPressHandler(verificaPressionado);
  btn2.setPressHandler(verificaPressionado);
  btn3.setPressHandler(verificaPressionado);
  btn4.setPressHandler(verificaPressionado);

  btn1.setReleaseHandler(aumentaOuDiminui);
  btn2.setReleaseHandler(aumentaOuDiminui);
  btn3.setReleaseHandler(aumentaOuDiminui);
  btn4.setReleaseHandler(aumentaOuDiminui);

}


void loop () {

  btn1.process();
  btn2.process();
  btn3.process();
  btn4.process();

// esperarDadosSerial();

}



void verificaPressionado(GFButton& botao) {
  int i;
  if (&botao == &btn1) 
	  i = 0;
  else if (&botao == &btn2) 
	  i = 1;
  else if (&botao == &btn3) 
	  i = 2;
  else if (&botao == &btn4) 
	  i = 3;


  temposPressionados[i] = millis();

}


void aumentaOuDiminui(GFButton& botao){
  int indice;
  if (&botao == &btn1) 
	  indice = 0;
  else if (&botao == &btn2) 
	  indice = 1;
  else if (&botao == &btn3) 
	  indice = 2;
  else if (&botao == &btn4) 
	  indice = 3;


  if ( millis() - temposPressionados[indice] > 1000) {
    if (qtd[indice] > 0) {
      diminuirContagem(botao, indice);
    } else {
      qtd[indice] = 0;
    }
  }
  else if (millis() - temposPressionados[indice] < 1000){
    aumentarContagem(botao, indice);
  }


}
//DUVIDA: será que colocar para salvar a cada vez que diminuir ou amentar a contagem nao irá deixar lento o processo?
//Talvez possa ter um timer para ver quando a pessoa parou de mexer ou colocar um quinto botao para quando a pessoa pressionar os dados sejam salvos
void aumentarContagem(GFButton& botao, int indice) {
  qtd[indice]++;
  atualizaTela(indice);
  salvarDadosNaEEPROM();
}
void diminuirContagem(GFButton& botao, int indice) {
  qtd[indice]--;
  atualizaTela(indice);
  salvarDadosNaEEPROM();
}

void mostrarPrimeiraColuna(){
	tela.setTextColor(TFT_WHITE);
  tela.setTextSize(3);
  tela.setCursor(15, 30);
  tela.print(contagem);

  for (int i = 0; i < 4; i++) {
    int y = 80 + i * altura ;

    tela.setCursor(15, y + i*5 + 15);

    escolheCor(i);

    tela.setTextSize(2);
    tela.print(contagem + " " + String(i + 1));
  }
}

void mostrarSegundaColuna() {
	tela.setTextColor(TFT_WHITE);
  tela.setTextSize(3);
  tela.setCursor(160, 30);
  tela.print("QTD");
  

	for (int i = 0; i < 4; i++) {
    int y = 90 + i * altura;
    if(qtd[i] < 10){
      space[i] = 55;
    }
    else if(qtd[i] >= 10 && qtd[i] < 100){
      space[i] = 38;
    }
    else if(qtd[i] >= 100 && qtd[i] < 1000){
      space[i] = 19;
    }
    else if(qtd[i] >= 1000 && qtd[i] < 9999){
      space[i] = 1;
    }
    
    Serial.println(String(unidades[i].length()));
    space[i] -= (unidades[i].length()*18); //largura da letra é 6 pixels no tamanho 3 = 18
    tela.setCursor(150 + space[i], y + i *6);  
    
    escolheCor(i);

    tela.setTextSize(3);
    tela.print(String(qtd[i])+unidades[i]);
    
  }
}

void atualizaTela(int i){
  int y = 90 + i * altura;
  if(qtd[i] < 10){
    space[i] = 55;
  }
  else if(qtd[i] >= 10 && qtd[i] < 100){
    space[i] = 38;
  }
  else if(qtd[i] >= 100 && qtd[i] < 1000){
    space[i] = 19;
  }
  else if(qtd[i] >= 1000 && qtd[i] < 9999){
    space[i] = 1;
  }
  
  tela.fillRect(110, y+ i *6, 120, 35, TFT_BLACK);
  space[i] -= (unidades[i].length()*18);
  tela.setCursor(150 + space[i], y + i *6);  
  
  escolheCor(i);
  tela.print(String(qtd[i])+unidades[i]);

  tela.setTextSize(3);
  

}

void escolheCor(int i){
  if (i == 0){
    tela.setTextColor(TFT_BLUE);
  }
  else if (i == 1){
    tela.setTextColor(TFT_RED);
  }
  else if (i == 2){
    tela.setTextColor(TFT_GREEN);
  }
  else if (i == 3){
    tela.setTextColor(TFT_YELLOW);
  }

}

void salvarDadosNaEEPROM() {
  // Salvar qtd[4]
  for (int i = 0; i < 4; i++) {
    EEPROM.put(enderecoQtd + i * sizeof(int), qtd[i]);
  }

  // Salvar contagem 
  byte tamanhoContagem = contagem.length(); //cada letra ocupa um byte
  EEPROM.put(enderecoContagem, tamanhoContagem);
  for (int i = 0; i < tamanhoContagem; i++) {
    EEPROM.put(enderecoContagem + 1 + i, contagem[i]);
  }

  // Salvar unidades[4] 
  int enderecoAtual = enderecoUnidades;
  for (int i = 0; i < 4; i++) {
    byte tam = unidades[i].length(); //tamanho da stirng de unidade 
    EEPROM.put(enderecoAtual++, tam); //salva o tamanho e move para o proximo endereco
    for (int j = 0; j < tam; j++) { //salva letra por letra
      EEPROM.put(enderecoAtual++, unidades[i][j]);
    }
  }
}

void carregarDadosDaEEPROM() {
  // Carregar qtd[4]
  for (int i = 0; i < 4; i++) {
    EEPROM.get(enderecoQtd + i * sizeof(int), qtd[i]);
  }

  byte tamanhoContagem; //cada letra ocupa um byte
  EEPROM.get(enderecoContagem, tamanhoContagem); //pega tamanho da string
  contagem = ""; //garante que a string contagem esta vazia 
  for (int i = 0; i < tamanhoContagem; i++) {
    char c;
    EEPROM.get(enderecoContagem + 1 + i, c);
    contagem += c;
  }

  // Carregar unidades[4]
  int enderecoAtual = enderecoUnidades;
  for (int i = 0; i < 4; i++) {
    byte tam; //tamanho da stirng de unidade 
    EEPROM.get(enderecoAtual++, tam); //pega o tamanho da string
    unidades[i] = ""; //garante que a string esta vazia 
    for (int j = 0; j < tam; j++) {
      char c;
      EEPROM.get(enderecoAtual++, c);
      unidades[i] += c;
    }
  }
}

void esperarDadosSerial() {
/*
QTD:10,20,30,40
Exemplo: NOME:SetorA
Exemplo: UNI:g,L,mm,kg
*/

  if (Serial.available() > 0) {
    String texto = Serial.readStringUntil('\n');
    texto.trim();

    if (texto.startsWith("QTD:")) {
      texto.remove(0, 4); // remove "QTD:"
      int i = 0;
      while (texto.length() > 0 && i < 4) {
        int pos_virgula = texto.indexOf(',');
        if (pos_virgula == -1){ //se não tiver virgula o resto da string sera o tamanho 
          pos_virgula = texto.length();
        } 
        qtd[i] = texto.substring(0, pos_virgula).toInt();
        texto.remove(0, pos_virgula + 1); //remove a parte usada e a virgula
        i++;
      }
      Serial.println("QTD recebida!");
    }

    else if (texto.startsWith("NOME:")) {
      texto.remove(0, 5); // remove "NOME:"
      contagem = texto;
      Serial.println("Nome recebido!");
    }

    else if (texto.startsWith("UNI:")) {
    texto.remove(0, 4); // remove "UNI:"
    int i = 0;
    while (texto.length() > 0 && i < 4) {
      int pos_virgula = texto.indexOf(',');
      if (pos_virgula == -1) { //se não tiver virgula o resto da string sera o tamanho -> ultimo valor digiado 
        pos_virgula = texto.length();
      }
      unidades[i] = texto.substring(0, pos_virgula); //pega string ate a posicao da virgula
      texto.remove(0, pos_virgula + 1); //remove a string usada e a virgula 
      i++;
    }
    Serial.println("Unidades recebidas!");
  }

  salvarDadosNaEEPROM()

}






