#include <Adafruit_GFX.h>
#include <MCUFRIEND_kbv.h>
#include <GFButton.h>
#include <EEPROM.h>


MCUFRIEND_kbv tela;
unsigned long temposPressionados[4] = {0, 0, 0, 0};
int space[4] = {0, 0, 0, 0};
String nome_contagem = "";
byte num = 0;

struct contagem{
  String nome ;
  String unidade;
  int passo;
  int qtd;
}contagem[4]; 


int altura = 50;
bool posicaoAnterior; 
bool posicao;
bool contagemAlterada = false;
unsigned long ultimaAlteracao = 0;
byte botao_press[100];


int tam_contagem = sizeof(contagem);
int tam_total = 0;
int tam_historico_botoes = 0;
int tam_botoes_historico_total = 0;


GFButton btn1(A8);
GFButton btn2(A9);
GFButton btn3(A10);
GFButton btn4(A11);

void setup() {

  Serial.begin(9600);
  carregarDadosDaEEPROM();
  esperarDadosSerial();

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

  esperarDadosSerial();

  if (contagemAlterada && (millis() - ultimaAlteracao > 5000)) {
    salvarDadosNaEEPROM();
    contagemAlterada = false;
    
    Serial.println("Dados salvos após 5 segundos");
    tam_historico_botoes = 0;
  }

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

    if (contagem[indice].qtd > 0) {
      diminuirContagem(botao, indice);
    } else {
      contagem[indice].qtd = 0;
    }
    botao_press[tam_historico_botoes] = -(indice + 1);
    
    Serial.println(botao_press[tam_historico_botoes]);
    tam_historico_botoes++;
  }
  else if (millis() - temposPressionados[indice] < 1000){
    aumentarContagem(botao, indice);
    botao_press[tam_historico_botoes] = (indice + 1);
    Serial.println(botao_press[tam_historico_botoes]);
    tam_historico_botoes++;
  }


}
void aumentarContagem(GFButton& botao, int indice) {
  contagem[indice].qtd++;
  atualizaTela(indice);
  contagemAlterada = true;
  ultimaAlteracao = millis();
}
void diminuirContagem(GFButton& botao, int indice) {
  contagem[indice].qtd--;
  atualizaTela(indice);
  contagemAlterada = true;
  ultimaAlteracao = millis();
}

void mostrarPrimeiraColuna(){
	tela.setTextColor(TFT_WHITE);
  tela.setTextSize(3);
  tela.setCursor(15, 30);
  tela.print(nome_contagem);

  for (int i = 0; i < num; i++) {
    int y = 80 + i * altura ;

    tela.setCursor(15, y + i*5 + 15);

    escolheCor(i);

    tela.setTextSize(2);
    tela.print(contagem[i].nome);
  }
}

void mostrarSegundaColuna() {
	tela.setTextColor(TFT_WHITE);
  tela.setTextSize(3);
  tela.setCursor(160, 30);
  tela.print("QTD");
  

	for (int i = 0; i < num; i++) {
    int y = 90 + i * altura;
    if( contagem[i].qtd < 10){
      space[i] = 55;
    }
    else if( contagem[i].qtd >= 10 && contagem[i].qtd < 100){
      space[i] = 38;
    }
    else if(contagem[i].qtd >= 100 && contagem[i].qtd < 1000){
      space[i] = 19;
    }
    else if(contagem[i].qtd >= 1000 && contagem[i].qtd < 9999){
      space[i] = 1;
    }
    
    Serial.println(String(contagem[i].unidade.length()));
    space[i] -= (contagem[i].unidade.length()*18); //largura da letra é 6 pixels no tamanho 3 = 18
    tela.setCursor(150 + space[i], y + i *6);  
    
    escolheCor(i);

    tela.setTextSize(3);
    tela.print(String(contagem[i].qtd)+contagem[i].unidade);
    
  }
}

void atualizaTela(int i){
  int y = 90 + i * altura;
  if(contagem[i].qtd < 10){
    space[i] = 55;
  }
  else if(contagem[i].qtd >= 10 && contagem[i].qtd < 100){
    space[i] = 38;
  }
  else if(contagem[i].qtd >= 100 && contagem[i].qtd < 1000){
    space[i] = 19;
  }
  else if(contagem[i].qtd >= 1000 && contagem[i].qtd < 9999){
    space[i] = 1;
  }
  
  tela.fillRect(110, y+ i *6, 120, 35, TFT_BLACK);
  space[i] -= (contagem[i].unidade.length()*18);
  tela.setCursor(150 + space[i], y + i *6);  
  
  escolheCor(i);
  tela.print(String(contagem[i].qtd)+contagem[i].unidade);

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
  //preciso salvar o titulo
  EEPROM.put(0, num);
  // Salvar num structs
  for (int i = 0; i < num; i++){
    EEPROM.put((tam_contagem * i) + 1, contagem[i]);
  }


  //salvar ordem de botoes pressionados 
  tam_total = (tam_contagem * num) + 1;
  EEPROM.put(tam_total + 1, tam_historico_botoes ); //por ser int ocupa 2 bytes
  
  for (int i = 0; i < tam_historico_botoes; i++ ){
    EEPROM.put(tam_total + 2 + i + tam_botoes_historico_total , botao_press[i]);
    
  }
  tam_botoes_historico_total += tam_historico_botoes;  
  
}


void carregarDadosDaEEPROM() {
  EEPROM.get(0, num);
  // Salvar num structs
  for (int i = 0; i < num; i++){
    EEPROM.get((tam_contagem * i) + 1, contagem[i]);
  }


  //salvar ordem de botoes pressionados 
  tam_total = (tam_contagem * num) + 1;
  EEPROM.get(tam_total + 1, tam_botoes_historico_total ); //por ser int ocupa 2 bytes
  
  for (int i = 0; i < tam_historico_botoes; i++ ){
    EEPROM.get(tam_total + 2 + i + tam_botoes_historico_total , botao_press[i]);
    
  }
  tam_botoes_historico_total += tam_historico_botoes;  
  EEPROM.put(tam_total + 1, tam_botoes_historico_total );
  
}


void esperarDadosSerial() {
  int pos_i;
  int pos_f;

  if (Serial.available() > 0) {
    String texto = Serial.readStringUntil('\n');
    texto.trim();
     
     //tenho que remover o [{ }] e depois de pegar o titulo apagar o contagens junto com o [{}]
    
    if (texto.startsWith("\"titulo\": ")){
      pos_i = texto.indexOf(" ");
      pos_f = texto.indexOf(",");
      nome_contagem = texto.substring(pos_i+2, pos_f-1); // "a", -> a
      texto.remove(0, pos_f+2); //remove até a virgula para no proximo pegar a virgula certa
      Serial.println(nome_contagem);
      Serial.println(texto);
      
    }

    if (texto.startsWith("\"num\": ")){
      pos_i = texto.indexOf(" ");
      pos_f = texto.indexOf(",");
      num = texto.substring(pos_i+2, pos_f-1).toInt();
      Serial.println(String(num));
      texto.remove(0, pos_f+ 2);
      Serial.println(texto);
    }

    int i = 0;
    while(i < num){
      if (texto.startsWith("\"nome\": ")){
        int pos_i = texto.indexOf(" ");
        int pos_f = texto.indexOf(",");
        contagem[i].nome = texto.substring(pos_i+2, pos_f-1);
        texto.remove(0, pos_f+2);
        Serial.println(contagem[i].nome);
      }
      if (texto.startsWith("\"passo\": ")){
        int pos_i = texto.indexOf(" ");
        int pos_f = texto.indexOf(",");
        contagem[i].passo = texto.substring(pos_i+2, pos_f-1).toInt();
        texto.remove(0, pos_f+2);
        Serial.println(String(contagem[i].passo));
      
      }

      if (texto.startsWith("\"unidade\": ")){
        int pos_i = texto.indexOf(" ");
        int pos_f = texto.indexOf(",");
        contagem[i].unidade = texto.substring(pos_i+2, pos_f-1);
        texto.remove(0, pos_f+2);
        Serial.println(contagem[i].unidade);
      }

      if (texto.startsWith("\"quantidade\": ")){
        int pos_i = texto.indexOf(" ");
        int pos_f = texto.indexOf("\n"); //nao tenho certeza
        contagem[i].qtd = texto.substring(pos_i+2, pos_f-1).toInt();
        texto.remove(0, pos_f+2);
        Serial.println(String(contagem[i].qtd));
      }
      atualizaTela(i); 

      i++;    
    }
    mostrarPrimeiraColuna();

  contagemAlterada = true;
  ultimaAlteracao = millis();
  
  }

}





