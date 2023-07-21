/**
 *          ESAME ELEMENTI DI PROGRAMMAZIONE (9 CFU)
 * NOME E COGNOME:  GIUSEPPE d'ANIELLO
 * MATRICOLA :      A13002119
 * DATA :           05/02/2020
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXR 20
#define MAX 100

struct Substring
{
    char substring[MAX];
    char precedente;
    int posizione;

}; typedef struct Substring substring;

int read(char t[][MAX], int *dim, char nomefile[])
{

    FILE *fp = fopen( nomefile, "r" );
    int d = 0;

    if ( fp == NULL )
        return -1;

    else

        while(! feof(fp) )
            fgets( t[d++], MAX, fp );

        fclose(fp);

        *dim = d;
        return 0;
}

void print(char t[][MAX], int dim)
{
    for(int i = 0; i < dim; i++ )
        printf("%s\n", t[i]);

    puts("");
}

void write(substring v[], int dim)
{

    FILE *fp = fopen( "output.bin", "w" );

    fwrite(v, sizeof(substring), dim, fp);

    fclose(fp);
}

void calcoloDoppie(char s[])
{
    int j;
    int i = 1;
    while( i < strlen(s) )
    {
        if (s[i] == s[i-1])
        {
            for(j = strlen(s)-1; j > i; j--)
            {
                    s[j] = s[j-1];
            }

            s[i] = '-';
        }
        i++;
    }
}

void sottostringa( char frase[], char temp[], int in, int fn)
{
    int i, j = 0;

    for(i = in; i < fn; i++)
        temp[j++] = frase[i];

    temp[j] = '\0';
}

void toStruct(char s[], substring v[], int in, int fn, int *k)
{
    int c = *k;

    sottostringa(s, v[*k].substring ,in, fn);

    v[c].posizione = in;

    if (c > 0)
        v[*k].precedente = s[in-1];

    else if (c == 0)
        v[c].precedente = '\0';

    *k = c+1;
}

int main( int *argc, char *argv[] )
{
    char testo[MAXR][MAX];      /* VETTORE DI STRINGHE */
    char nomefile[MAX];         /* NOME DEL FILE DA APRIRE */
    int numrighe = 0;           /* CONTATORE PER NUMERO RIGHE DEL TESTO*/
    substring v[MAX];           /* VETTORE DI STRUCT */
    int i;                      /* CONTATORE GENERICO */
    int in, fn;                 /* CONTATORE PER CALCOLO SOTTOSTRINGA */
    int contachar;              /* CONTATORE PER NUMERO CARATTERI*/
    int k = 0;                  /* CONTATORE PER NUMERO DI ELEMENTI DEL VETTORE DI STRUCT */

    /*
    printf("INSERISCI NOME FILE DA APRIRE: ");
    fscanf( stdin, "%s", nomefile );
    */

    if ( read(testo, &numrighe, "testo.txt") == 0 )
    {
        printf("\t\tTESTO ORIGINALE\n");
        printf("\t\t");
        print(testo, numrighe);

        for(i = 0; i < numrighe; i++)
            calcoloDoppie(testo[i]);

        printf("\t\tTESTO ELABORATO\n");
        printf("\t\t");
        print(testo, numrighe);

        /* CICLO CHE SCORRE LE DIVERSE RIGHE DI TESTO */
        for(i = 0; i < numrighe; i++)
        {
            /*INIZIALIZZAZIONE CONTATORI*/
            in = 0;
            fn = 0;
            contachar = 0;

            /* CICLO CHE SCORRE LA SINGOLA STRINGA */
            do
            {
                contachar++;

                if( testo[i][fn] == '-')
                {
                    contachar = 0;
                    toStruct(testo[i], v, in, fn, &k);
                    in = fn + 1;
                }
                else if( testo[i][fn] == '.' )
                {
                    contachar = 0;
                    toStruct(testo[i], v, in, fn, &k);
                    in = fn + 1;
                }
                else if( testo[i][fn] == ' ' && contachar >= 20)
                {
                    contachar = 0;
                    toStruct(testo[i], v, in, fn, &k);
                    in = fn + 1;
                }

                fn++;

            } while ( testo[i][fn] != '\0' );
        }
        puts("");

        /* STAMPA DEI RISULTATI OTTENUTI */
        for(i = 0; i < k; i++)
        {
            printf("\t\t\tELEMENTO %d\n\n", i);
            printf("\t\tSOTTOSTRINGA:\t%s\n", v[i].substring );
            printf("\t\tPOSIZIONE :\t%d\n", v[i].posizione );
            printf("\t\tCARATTERE PRECEDENTE:\t%c\n", v[i].precedente);
            puts("");
        }

        /* SCRITTURA SU FILE BINARIO */
        write(v, k);
        return EXIT_SUCCESS;
    }
    else
    {
         printf("IL FILE NON ESISTE...");
         return EXIT_FAILURE;
    }
}
