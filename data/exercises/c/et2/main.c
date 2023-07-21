/*

NOME: Orlando
COGNOME: Autiero
MATRICOLA: A13001589

*/

#include <stdio.h>
#define dim 100

typedef enum q {false=0, true=1} bool; //Attraverso un enum rinomizzata, mi dichiaro il tipo bool per il bubble sort

typedef struct qq {
    float avg; //Media della riga/colonna
    char id; //Identificatore 'r' o 'c'
    int rc; //Identificatore per il numero di riga/colonna
} stt; //stt sarà l'identificatore di tipo della mia struct

int readFile(float m[][dim], int *r, int *c); //Funzione per leggere da file
int avgRowCol(float m[][dim], int r, int c, stt v[dim]); //Funzione per il calcolo della media e riempimento della struct
void printMat(float m[][dim], int r, int c); //Funzione per stampare la matrice letta
void sortStruct(stt v[dim], int n); //Funzione per l'ordinamento della struct --BUBBLE SORT--
int writeFile(stt v[dim], int n); //Funzione per scrivere sul file
int checkBin(int); //Funzione per controllare l'output sul file
void printStruct(stt v[dim], int n); //Funzione per stampare le struct generate
void swap (stt *a, stt *b); //Scambio di due struct attraverso i loro indirizzi

int readFile(float m[][dim], int *r, int *c) {
    FILE *fp=NULL; //Puntatore al file
    int ri=0; //Risultato di avvenuta lettura
    if(fp=fopen("input.txt", "r")) { //Se il file viene aperto
        fscanf(fp, "%d %d\n\n", r, c); //Leggo le due dimensioni
        for(int i=0; i<*r; i++) {
            for(int j=0; j<*c; j++) {
                if(j==(*c-1)) fscanf(fp, "%f\n", &m[i][j]); //Se mi trovo all'ultimo elemento, leggo e vado a capo
                else fscanf(fp, "%f ", &m[i][j]); //Se non mi trovo all'ultimo elemento, leggo e vado avanti
            }
        }
        fclose(fp); //Chiusura del file
        ri=1; //Lettura effettuata
    }
    return ri; //Ritorno avvenuta lettura
}

void printMat(float m[][dim], int r, int c) {
    printf("\n\n");
    for(int i=0; i<r; i++) {
        for(int j=0; j<c; j++) {
            printf("%0.1f  ", m[i][j]); //Stampa della mia matrice con un numero decimale dopo la virgola
        } printf("\n");
    } printf("\n");
}

int avgRowCol(float m[][dim], int r, int c, stt v[dim]) {
    float avg=0; //Variabile per la media
    int n=0, i=0, j=0;
    for(i=0; i<r; i++) { //Ciclo per le righe
        for(j=0; j<c; j++) avg+=m[i][j]; //Mi calcolo la somma temporanea
        avg/=c; //La divido per il numero di elementi presente su ogni riga
        v[n].avg=avg; //Assegno la media alla struct di posto n
        v[n].id='r'; //Assegno l'identificatore 'r' alla struct di posto n
        v[n].rc=i; //Assegno il numero di riga per la quale si è calcolata la media
        n++; //Incremento n per avere la prossima struct
        avg=0; //Resetto la media a 0 per il prossimo calcolo
    }
    for(i=0; i<c; i++) { //Ciclo per le colonne
        for(j=0; j<r; j++) avg+=m[j][i]; //Mi calcolo la somma temporanea
        avg/=r; //La divido per il numero di elementi in ogni colonna
        v[n].avg=avg; //Assegno la media alla struct di posto n
        v[n].id='c'; //Assegno l'identificatore 'c' alla struct di posto n
        v[n].rc=i; //Assegno il numero di colonna per la quale si è calcolata la media
        n++; //Incremento n per avere la prossima struct
        avg=0; //Resetto avg a 0 per il prossimo calcolo
    }
    return n; //Ritorno n, che è il numero di struct riempite nell'array di struct
}

void printStruct(stt v[dim], int n) {
    for(int i=0; i<n; i++) { //Stampo la struct
        printf("Istanza di struct generata: ");
        printf("\n\tMedia: %0.2f", v[i].avg);
        printf("\n\tIdentificatore: %c", v[i].id);
        printf("\n\tRiga/colonna corrispondente: %d\n\n", v[i].rc);
    }
}

void sortStruct(stt v[dim], int n) {
    bool b; //Variabile booleana per la condizione d'uscita del bubble sort
    do {
        b=false;
        for(int i=0; i<n-1; i++) {
            if(v[i].avg>v[i+1].avg) { //Se la media della struct di posto i, è maggiore della media della struct di posto i+1
                swap(&v[i], &v[i+1]); //Scambio i loro indirizzi di memoria
                b=true; //Imposto b a true, che significa modifica alla struct effettuata
            }
        }
    } while (b); //Esegui il ciclo do-while finché faccio modifiche
}

void swap (stt *a, stt *b) {
    stt c; //Struttura temporanea per l'appoggio dei dati
    c=*a; //Scambio
    *a=*b; //Scambio
    *b=c; //Scambio
}

int writeFile(stt v[dim], int n) {
    FILE *fp=NULL; //Puntatore al file
    int r=0; //Risultato di ritorno
    fp=fopen("output.bin", "w");
    if (fp!=NULL) { //Se il file viene apero
        //fwrite(&n, sizeof(int), 1, fp); //Scrivo la dimensione del mio array
           printf("%dnnnnnnnnnnnnnnnn\n",n);
        for(int i=0; i<n; i++) 
          fwrite(&v[i], sizeof(stt), 1, fp); //E per ogni struct, la salvo sul file
        
        fclose(fp); //Chiudo il file
        r=1; //Scrittura effettuata
    } return r; //Ritorno del risultato
}

int checkBin(int n) {
    FILE *fp=NULL; //Puntatore al file
    int r=0; //Risultato, numero di struct
    stt vv[dim]; //Nuova struttura su cui mettere i dati letti
      fp=fopen("output.bin", "r");
    if (fp!=NULL) { 
		//fread(&n, sizeof(int), 1, fp); //Leggo la dimensione della struct
        for(int i=0; i<n; i++) fread(&vv[i], sizeof(stt), 1, fp); //Leggo le struct
        fclose(fp); //Chiudo il file
        printf("\nStruct lette da file binario:\n\n"); printStruct(vv, n); //Stampo l'avvenuta lettura
        r=1; //Lettura effettuata
    } return r; //Ritorno di r
}

int main() {
    float m[dim][dim]={0}; //Matrice di reali di dimensione dim, dim
    int r=0, c=0, n=0; //Righe, colonne, elementi della struct
    stt v[dim*2]; //Struct, ha dimensione dim*2 perché conterrà massimo dim righe e dim colonne
   // char cc; //Variabile di controllo per la richiesta del controllo dell'output
    if(readFile(m, &r, &c)) { //Se readFile mi ritorna 1, ho letto il file
        printf("Matrice letta da file: "); printMat(m, r, c); //Stampo la matrice letta
        n=avgRowCol(m, r, c, v); //Calcolo la media di righe e di colonne, e mi ritorna il numero degli elementi della struct
        sortStruct(v, n); //Ordino la mia struct
        printf("Istanze di struct ordinate per valori crescenti di media:\n\n"); printStruct(v, n); //Stampo le struct generate e ordinate
       writeFile(v, n);
        printf("%dnnnnnnnnnnnnnnnn\n",n);
        checkBin(n);
	
    } else printf("Impossibile aprire file 'input.txt' per la lettura."); //In caso di errore per l'apertura del file in lettura
    return 0;
} //Fine

