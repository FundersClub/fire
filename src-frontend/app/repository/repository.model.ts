import { EmailMap } from './email-map.model';

export class Repository {
  constructor(
    public emailmap_set: Array<EmailMap>,
    public email_slug: string,
    public login: string,  // Owner of repo
    public name: string,
    public status: string, // "active", "pending-accept", "pending-inviter-approval"
    public url: string
  ) {}
}


// {
//     "emailmap_set": [
//         {
//             "email": "alexandre.scialom@gmail.com",
//             "login": "youpdidou",
//             "repo": "http://localhost:12000/api/github/repository/4/",
//             "url": "http://localhost:12000/api/github/email-map/3/"
//         },
//         {
//             "email": "alexandre@fundersclub.com",
//             "login": "youpdidou",
//             "repo": "http://localhost:12000/api/github/repository/4/",
//             "url": "http://localhost:12000/api/github/email-map/4/"
//         }
//     ],
//     "email_slug": "46f48eac",
//     "login": "youpdidou",
//     "name": "buzz",
//     "status": "active", "pending-accept", "pending-inviter-approval",
//     "url": "http://localhost:12000/api/github/repository/4/"
// }
