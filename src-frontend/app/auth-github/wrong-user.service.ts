import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Http } from '@angular/http';

import 'rxjs/add/operator/toPromise';

import { Repository } from '../repository/repository.model';
import { RepositoryService } from '../repository/repository.service';
import { UserIsAuthedGuard } from '../user-auth.service';

@Injectable()
export class UserCantApproveRepoGuard implements CanActivate {
    constructor(
        private http: Http,
        private repositoryService: RepositoryService,
        private authGuard: UserIsAuthedGuard,
        private router: Router
    ) {}

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
        let uuid = route.params['uuid'];
        let url = `/api/github/repository/${uuid}/approve/`;

        // Only run this check if user successfully logged in.
        return this.authGuard.canActivate(route, state).then((auth: boolean) => {
            if(!auth) {
               return false;
            } else {
                return this.http.post(url, {uuid: uuid}).toPromise()
                    .then((response) => {
                        let repo = response.json() as Repository;
                        // Add repo to list. Only reason it would already be there is because
                        // you're a dev testing this flow. But will check anyways.
                        if (!this.repositoryService.getByUrl(repo.url)) {
                            this.repositoryService.add(repo);
                        }
                        // If repo is now active, send em' over.
                        if (repo.status == 'active') {
                            this.router.navigate(['/repos', repo.login, repo.name, 'set-up', 'email']);
                            return false;
                        // Otherwise, give em them bad news.
                        } else {
                            return true;
                        }
                    })
                    .catch((error: any) => {
                        // Usually a 404.
                        // User is authenticated, so we'll redirect them somewhere useful.
                        this.router.navigate(['/repos']);
                        return false;
                    });
            }
        });
    }
}
