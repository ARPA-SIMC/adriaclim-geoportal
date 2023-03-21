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
