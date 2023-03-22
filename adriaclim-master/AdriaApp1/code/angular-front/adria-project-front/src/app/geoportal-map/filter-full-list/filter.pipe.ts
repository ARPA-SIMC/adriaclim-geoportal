// filter.pipe.ts

import { Pipe, PipeTransform } from '@angular/core';

// interface Node {
//   name: string;
// }

@Pipe({ name: 'appFilter' })
export class FilterPipe implements PipeTransform {
  /**
   * Pipe filters the list of elements based on the search text provided
   *
   * @param items list of elements to search in
   * @param searchText search string
   * @returns list of elements filtered by search text or []
   */
  transform(items: any[] , searchText: string): any[] {
    if (!items) {
      return [];
    }
    if (!searchText) {
      return items;
    }

      //items is an array
      searchText = searchText.toLocaleLowerCase();
      return items.filter(it => {
        let name = it.name.title.toLocaleLowerCase();
        const searchWords: string[] = searchText.split(' ');
        return  searchWords.every(searchWord => name.includes(searchWord)) || it.name.institution.toLocaleLowerCase().includes(searchText);
      });


  }



}
// @Pipe({ name: 'appFilterDataset' })
// export class FilterPipeDataset implements PipeTransform {
//   /**
//    * Pipe filters the list of elements based on the search text provided
//    *
//    * @param items list of elements to search in
//    * @param searchText search string
//    * @returns list of elements filtered by search text or []
//    */
//   transform(items: any[] , searchText: string): any[] {
//     if (!items) {
//       return [];
//     }
//     if (!searchText) {
//       return items;
//     }

//       //items is an array
//       searchText = searchText.trim().toLocaleLowerCase();
//       return items.filter(it => {
//         let name = it.name.title.toLocaleLowerCase();
//         let institution = it.name.institution.toLocaleLowerCase();
//         const searchWords: string[] = searchText.split(' ');
//         return  searchWords.every(searchWord => name.includes(searchWord)) || institution.includes(searchText);
//       });
//   }

// }
