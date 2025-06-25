#include <Adafruit_GFX.h>
#include <MCUFRIEND_kbv.h>
#include <GFButton.h>
#include <EEPROM.h>


MCUFRIEND_kbv tela;
unsigned long temposPressionados[4] = {0, 0, 0, 0};
int space[4] = {0, 0, 0, 0};
char titulo[20] = "";
byte num = 0;

struct contagem{
  char nome[20];
  char unidade[3];
  int passo;
  int qtd = -2;
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
    
    //Serial.println("Dados salvos após 5 segundos");

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

  if (contagem[indice].qtd != -1 && contagem[indice].qtd != -2){
    if ( millis() - temposPressionados[indice] > 1000) {
      if (contagem[indice].qtd > 0) {
        diminuirContagem(botao, indice);
      } else {
        contagem[indice].qtd = 0;
      }
      botao_press[tam_historico_botoes] = -(indice + 1);
      
      //Serial.println(botao_press[tam_historico_botoes]);
      tam_historico_botoes++;
    }
    else if (millis() - temposPressionados[indice] < 1000){
      aumentarContagem(botao, indice);
      botao_press[tam_historico_botoes] = (indice + 1);
      //Serial.println(botao_press[tam_historico_botoes]);
      tam_historico_botoes++;
    }
  }


}
void aumentarContagem(GFButton& botao, int indice) {
  contagem[indice].qtd += contagem[indice].passo;
  atualizaTela(indice);
  contagemAlterada = true;
  ultimaAlteracao = millis();
}
void diminuirContagem(GFButton& botao, int indice) {
  contagem[indice].qtd -= contagem[indice].passo;
  atualizaTela(indice);
  contagemAlterada = true;
  ultimaAlteracao = millis();
}

void mostrarPrimeiraColuna(){
	tela.setTextColor(TFT_WHITE);
  tela.setTextSize(3);
  tela.setCursor(15, 30);
  tela.print(titulo);

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

    if(contagem[i].qtd != -1){
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
      
      //Serial.println(strlen(contagem[i].unidade));
      space[i] -= (strlen(contagem[i].unidade)*18); //largura da letra é 6 pixels no tamanho 3 = 18
      tela.setCursor(150 + space[i], y + i *6);  
      
      escolheCor(i);
      tela.setTextSize(3);
      tela.print(String(contagem[i].qtd)+contagem[i].unidade);
    }
      
      
      

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
  space[i] -= (strlen(contagem[i].unidade)*18);
  tela.setCursor(150 + space[i], y + i *6);  
  
  escolheCor(i);
  tela.print(String(contagem[i].qtd)+contagem[i].unidade);

  tela.setTextSize(3);
  

}

void atualizaTelaSerial() {
  tela.fillScreen(TFT_BLACK); 
  mostrarPrimeiraColuna();   
  mostrarSegundaColuna();     
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
  int tam_titulo = strlen(titulo) + 1; // \0
  EEPROM.put(0, titulo);
  
  
  EEPROM.put(tam_titulo, num);
  // Salvar num structs
  for (int i = 0; i < num; i++){
    EEPROM.put(tam_titulo + sizeof(int) + (tam_contagem * i) + 1, contagem[i]);
  }
  //salvar ordem de botoes pressionados 
  tam_total = tam_titulo + (tam_contagem * num) + 1;
  EEPROM.put(tam_total + 1, tam_historico_botoes ); //por ser int ocupa 2 bytes
  
  for (int i = 0; i < tam_historico_botoes; i++ ){
    EEPROM.put(tam_total + sizeof(int) + i + tam_botoes_historico_total , botao_press[i]);
  }
  tam_botoes_historico_total += tam_historico_botoes;  
  
}


void carregarDadosDaEEPROM() {
  
  EEPROM.get(0, titulo);
  
  int tam_titulo = strlen(titulo) + 1; //

  EEPROM.get(tam_titulo, num);

  // Salvar num structs
  for (int i = 0; i < num; i++){
    EEPROM.get(tam_titulo + sizeof(int) + (tam_contagem * i) + 1, contagem[i]);
  }

  //salvar ordem de botoes pressionados 
  tam_total = tam_titulo + (tam_contagem * num) + 1;
  EEPROM.get(tam_total + 1, tam_historico_botoes ); //por ser int ocupa 2 bytes
  
  for (int i = 0; i < tam_historico_botoes; i++ ){
    EEPROM.get(tam_total + sizeof(int) + i + tam_botoes_historico_total , botao_press[i]);
  }
  tam_botoes_historico_total += tam_historico_botoes; 

  EEPROM.put(tam_total + 1, tam_botoes_historico_total );
  
}
void enviarDadosSerial(){

  String texto = String(titulo) + ", " + String(num);

  int i = 0;
  while(i < num){
    texto += ", " + String(contagem[i].nome) + ", " +  String(contagem[i].passo) + ", " + String(contagem[i].unidade) + ", " + String(contagem[i].qtd);
    i++;
  }

  texto += ", historico";
  int j = 0;
  while(j < tam_botoes_historico_total){
    
    texto += ", " + String(botao_press[j]);
    j++;
  }

 


}

void esperarDadosSerial() {
  // titulo, num, nome, passo, unidade, quantidade ...
  // Setor, 3, setorA, 1, kg, 10, setorB, 2, g, 2, setorC, 4, mm, 0
  int pos_f;

  if (Serial.available() > 0) {
    String texto = Serial.readStringUntil('\n');
    texto.trim();

    if(texto.startsWith("configurar ")){
      texto.remove(0,11);
      //Serial.println("texto: ");
      //Serial.println(texto);
      

      pos_f = texto.indexOf(",");
      String titulo_str = texto.substring(0, pos_f); // a, -> a
      strcpy(titulo, titulo_str.c_str());
      texto.remove(0, pos_f+1); //remove até a virgula para no proximo pegar a virgula certa
      //Serial.println(titulo);
      //Serial.println(texto);

      pos_f = texto.indexOf(",");
      num = texto.substring(0, pos_f).toInt();
      //Serial.println(String(num));
      texto.remove(0, pos_f + 1);
      //Serial.println(num);
      //Serial.println(texto);

      for (int j = 0; j < num; j++) {
        contagem[j].qtd = -1;
      }

      int i = 0;
      while(i < num){
      
        pos_f = texto.indexOf(",");
        String nome_str = texto.substring(0, pos_f);
        strcpy(contagem[i].nome, nome_str.c_str());
        texto.remove(0, pos_f+1);
        //Serial.println(contagem[i].nome);
        //Serial.println(texto);

        pos_f = texto.indexOf(",");
        contagem[i].passo = texto.substring(0, pos_f).toInt();
        texto.remove(0, pos_f+1);
        //Serial.println(String(contagem[i].passo));
        //Serial.println(texto);

        pos_f = texto.indexOf(",");
        String unidade_str = texto.substring(0, pos_f);
        strcpy(contagem[i].unidade, unidade_str.c_str());
        texto.remove(0, pos_f+1);
        //Serial.println(contagem[i].unidade);
        //Serial.println(texto);
        
        pos_f = texto.indexOf(",");
        if (pos_f == -1){ //Último valor, não tem mais vírgula
          contagem[i].qtd = texto.toInt();
          texto = ""; 
        } else{
          contagem[i].qtd = texto.substring(0, pos_f).toInt();
          texto.remove(0, pos_f+1);
        }
        //Serial.println(String(contagem[i].qtd));
        //Serial.println(texto);
      
        i++;    
      }
    
      atualizaTelaSerial(); 
    }
    if(texto.startsWith("enviar")){
      enviarDadosSerial();

    }

  contagemAlterada = true;
  ultimaAlteracao = millis();
  
  }

}



