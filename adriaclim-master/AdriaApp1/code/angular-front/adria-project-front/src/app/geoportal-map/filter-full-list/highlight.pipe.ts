import { Directive, Input, SimpleChanges, Renderer2, ElementRef, OnChanges } from '@angular/core';

@Directive({
  selector: '[appHighlight]'
})
export class HighlightDirective implements OnChanges {
  @Input() searchedWord!: string; // searchText
  @Input() content!: any; // HTML content
  @Input() classToApply!: string; //class to apply for highlighting
  @Input() setTitle = false; //sets title attribute of HTML

  constructor(private el: ElementRef, private renderer: Renderer2) {
    // this.content = this.content.name.title;


   }

  ngOnChanges(changes: SimpleChanges): void {
    if (!this.content) {
      return;
    }

    if (this.setTitle) {
      this.renderer.setProperty(
        this.el.nativeElement,
        'title',
        this.content
      );
    }

    if (!this.searchedWord || !this.searchedWord.length || !this.classToApply) {
      this.renderer.setProperty(this.el.nativeElement, 'innerHTML', this.content);
      return;
    }



    this.renderer.setProperty(
      this.el.nativeElement,
      'innerHTML',
      this.getFormattedText()
    );
  }

  getFormattedText() {
    const re = new RegExp(`(${this.searchedWord})`, 'gi');
    let rep = this.content.replace(re, `<span style="${this.classToApply}">$1</span>`);

    return rep
  }
}
