import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { MdTabNavBar } from '@angular/material';

import { Repository } from './repository.model';

@Component({
    styleUrls: ['./repository.component.css'],
    templateUrl: './repository.component.html',
})
export class RepositoryComponent implements OnInit, AfterViewInit {
    repo: Repository;
    @ViewChild(MdTabNavBar) private tabs: MdTabNavBar;

    constructor(
        private route: ActivatedRoute
    ) {}

    ngOnInit() {
        this.route.data.subscribe((data: { repository: Repository }) => {
            this.repo = data.repository;
        });
    }

    ngAfterViewInit() {
        // mdInkBar has a nasty bug which makes it misaligned on load.
        // https://github.com/angular/material2/issues/3133
        // This triggers a reposition immediately after rendering.
        setTimeout(() => {
            this.tabs._activeLinkChanged = true;
            this.tabs.ngAfterContentChecked();
        }, 10);
    }
}
