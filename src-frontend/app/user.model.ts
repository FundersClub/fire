import { Repository } from './repository/repository.model';

export class User {
  constructor(
    public is_authenticated: boolean,
    public username?: string, // Github username
    public repositories?: Array<Repository>,
    public urls?: {[route: string]: string}
  ) {}
}

// /api/github/me/
// {
//     "username": "youpdidou",
//     "is_authenticated": true,
//     "repositories": [
//         {
//             "emailmap_set": [
//                 {
//                     "email": "alexandre.scialom@gmail.com",
//                     "login": "youpdidou",
//                     "repo": "http://localhost:12000/api/github/repository/4/",
//                     "url": "http://localhost:12000/api/github/email-map/3/"
//                 },
//                 {
//                     "email": "alexandre@fundersclub.com",
//                     "login": "youpdidou",
//                     "repo": "http://localhost:12000/api/github/repository/4/",
//                     "url": "http://localhost:12000/api/github/email-map/4/"
//                 }
//             ],
//             "email_slug": "46f48eac",
//             "login": "youpdidou",
//             "name": "buzz",
//             "status": "active",
//             "url": "http://localhost:12000/api/github/repository/4/"
//         }
//     ],
//     "urls": {
//         "logout": "http://localhost:12000/accounts/logout/"
//     }
// }
