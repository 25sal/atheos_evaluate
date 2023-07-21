#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Mystruct
{
	char lettera;
	float frequenzaOccorrenza;	
	int numeroOccorrenze;
	int posizioniLettera[100];
};


void printstruct(struct Mystruct v)
{


	printf("{%c, %f, %d, [",v.lettera, v.frequenzaOccorrenza, v.numeroOccorrenze);
	for(int i=0;i<v.numeroOccorrenze;i++)
		printf("%d,", v.posizioniLettera[i]);
	printf("]}\n");
	
	}

void leggiStringa(char *stringa, char *dest); //leggi la stringa eliminando i caratteri duplicati
int occorrenzeCarattere(char *str, char c);
float frequenzaCarattere(char *str, char c);
void leggiPosizioniCaratteriInVettore(char *str, char c, int *vet); //punto 3; il vettore è da considerarsi finito quando si raggiunge il carattere -1;
void printStructVect(struct Mystruct *stringhe, int len); //stampa il vettore di strutture

int main(){
	char stringa[100];
	FILE *input;
	input=fopen("input.txt", "r"); //apre il file in lettura
	if(input==NULL)
	{
		printf("Errore durante l'apertura del file in input! Inserire la stringa manualmente:\n> ");
		fgets(stringa, 100, stdin);
	}
	else
	{
		fgets(stringa, 100, input);
	}
	fclose(input);
	
	int l = strlen(stringa);
	if(stringa[l - 1] == '\n') stringa[l-- - 1] = 0; //se l'ultimo carattere è il terminatore di riga, lo rimuovo e decremento l
	
	char stringaNorm[100];
	leggiStringa(stringa, stringaNorm);
	int lN = strlen(stringaNorm);
	struct Mystruct dettagliStringa[100];
	int i;
	for(i = 0; i < lN; i++)
	{
		dettagliStringa[i].lettera = stringaNorm[i];
		dettagliStringa[i].frequenzaOccorrenza = frequenzaCarattere(stringa, stringaNorm[i]);
		dettagliStringa[i].numeroOccorrenze = occorrenzeCarattere(stringa, stringaNorm[i]);
		leggiPosizioniCaratteriInVettore(stringa, stringaNorm[i], dettagliStringa[i].posizioniLettera);
	}
	printStructVect(dettagliStringa, lN);
	
	FILE *output;
	output=fopen("output.bin", "w"); //apre il file in scrittura
	if(output==NULL)  //se l'apertura non avviene correttamente
	{ 
		printf("Errore durante l'apertura del file in output\n");
		exit(1);
	}
	fwrite(dettagliStringa, sizeof(struct Mystruct), lN, output);
	fclose(output);
	output=fopen("output.bin", "r"); //apre il file in scrittura
	fread(dettagliStringa, sizeof(struct Mystruct), lN, output);
	for(int i=0;i<lN;i++)
	  printstruct(dettagliStringa[i]);

}

void leggiStringa(char *stringa, char *dest)
{
	char c;
	int i = 0, ni = 0;
	int exists;
	do
	{
		exists = 0;
		c = stringa[i];
		int j;
		for(j = 0; j < i; j++)
		{
			if(stringa[j] == c)
			{
				exists = 1;
				break;
			}
		}
		if(!exists) dest[ni++] = c;
		i++;
	} while (c != 0);
}
int occorrenzeCarattere(char *str, char c)
{
	int l = strlen(str);
	int occ = 0;
	int i;
	for(i = 0; i < l; i++)
	{
		if(str[i] == c) occ++;
	}
	return occ;
}
float frequenzaCarattere(char *str, char c)
{
	float occorrenze = occorrenzeCarattere(str, c);
	
	return occorrenze / strlen(str);
}
void leggiPosizioniCaratteriInVettore(char *str, char c, int *vet)
{
	int l = strlen(str);
	int vPos = 0;
	int i;
	for(i = 0; i < l; i++)
	{
		if(str[i] == c) vet[vPos++] = i;
	}
	vet[vPos] = -1;
}
void printStructVect(struct Mystruct *stringhe, int len)
{
	int i, j;
	for(i = 0; i < len; i++)
	{
		printf("'%c', %i, %f, [", stringhe[i].lettera, stringhe[i].numeroOccorrenze,  stringhe[i].frequenzaOccorrenza);
		j = 0;
		while(stringhe[i].posizioniLettera[j] != -1)
		{
			printf("%i", stringhe[i].posizioniLettera[j]);
			if(stringhe[i].posizioniLettera[++j] != -1) printf(",");
		}
		printf("]\n");
	}
}
