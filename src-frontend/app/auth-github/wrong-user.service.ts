import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot } from '@angular/router';
import { Http } from '@angular/http';

import 'rxjs/add/operator/toPromise';

import { Repository } from '../repository/repository.model';

@Injectable()
export class UserCantApproveRepoGuard implements CanActivate {
    constructor(
        private http: Http,
        private router: Router
    ) {}

    canActivate(route: ActivatedRouteSnapshot) {
        let uuid = route.params['uuid'];
        let url = `/api/github/repository/${uuid}/approve/`;
        return new Promise((resolve, reject) => {
            this.http.post(url, {uuid: uuid}).toPromise()
                .then((response) => {
                    let repo = response.json() as Repository;
                    console.log(repo);
                    // If repo is now active, send em' over. Otherwise, give em them bad news.
                    if (repo.status == 'active') {
                        this.router.navigate(['/repos', repo.login, repo.name]);
                        resolve(false);
                    } else {
                        resolve(true);
                    }
                })
                .catch((error: any) => {
                    // Usually a 404.
                    // User is authenticated, so we'll redirect them somewhere useful.
                    this.router.navigate(['/repos']);
                    resolve(false);
                });
            });
    }
}
