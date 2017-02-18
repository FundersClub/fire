import os
import html2text

from bs4 import BeautifulSoup

from django.conf import settings


def msg_to_markdown(repo, msg):
    def absurl(url):
        if not url.startswith('http:/') and not url.startswith('https:'):
            slash = '' if settings.BASE_URL.endswith('/') or url.startswith('/') else '/'
            return settings.BASE_URL + slash + url
        return url

    # Need a map of content id -> attachment
    all_attachments = list(msg.attachment_set.all())
    attachments_map = {}
    for att in all_attachments:
        if att.content_id:
            attachments_map[att.content_id] = att

    # Attempt to update img elements pointing to an attach,ment
    attachments_observed = set()
    if msg.body_html:
        soup = BeautifulSoup(msg.body_html, 'html.parser')
        for img in soup.find_all('img'):
            src = img.attrs.get('src')
            if not src or not src.startswith('cid:'):
                continue

            att = attachments_map.get(src.replace('cid:', ''))
            if att:
                img['src'] = att.file.url
                attachments_observed.add(att)

        h = html2text.HTML2Text(bodywidth=0)
        msg_body = h.handle(str(soup))
    else:
        msg_body = msg.body_text

    # Look for attachments we didn't display inline
    attachments = list(att for att in all_attachments if att not in attachments_observed)
    if attachments:
        attachments_text = u'\n\n\n\n---\n*Attachments:*\n\n'
        for att in attachments:
            url = att.file.url
            filename = os.path.basename(att.file.name)
            inline_img = ''
            if filename.lower().split('.')[-1] in ('png', 'gif', 'jpeg', 'jpg' 'svg'):
                inline_img = u'\n  ![]({})\n'.format(url)
            attachments_text += u'1. [{}]({}){}\n'.format(filename, url, inline_img)
    else:
        attachments_text = ''

    # See if we recognize this email address
    map_entry = repo.emailmap_set.filter(email__iexact=msg.from_email).first()
    if map_entry:
        tag = '@' + map_entry.login
    else:
        tag = msg.from_name

    return u'*Opened via [firebot]({}/), sent by {} ({})*\n\n{}{}'.format(
        settings.BASE_URL,
        tag,
        msg.from_email,
        msg_body,
        attachments_text,
    )
