/**
 * Funzione utilizzata per impostare la prima lettera di una parola in maiuscolo e le successive in minuscolo
 */
export function titleCaseWord(word: string): string {
  return word[0].toUpperCase() + word.substring(1).toLowerCase();
}
