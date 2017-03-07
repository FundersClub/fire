import { Component } from '@angular/core';

@Component({
  template: `
      <md-card class="SectionCard">
          <div class="CardIntro">
              <div class="CardIntro-title">
                  Page not found
              </div>
              <div class="CardIntro-subtext">
                  We couldn't find the page you were looking for.
              </div>
          </div>
      </md-card>
  `
})
export class PageNotFoundComponent {}
