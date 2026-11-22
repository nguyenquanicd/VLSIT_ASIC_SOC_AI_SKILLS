# Source qualification and search protocol

## Product documents

Count only a manufacturer, standards body or authorized design-house datasheet/databook that describes the target feature in a real product or documented design. Record document title, organization, product/family key, revision, date, language, stable URL, exact access basis, local filename, file hash and relevant pages. An application note can contextualize a feature but does not count toward the ten datasheet/databook threshold. Marketing summaries, product landing pages and search snippets do not count.

Use distinct product-family keys. A revision, language translation, mirror or companion datasheet for the same family does not add another product. Record separately branded families only when the source documents establish that they are distinct products, not relabelings of one design.

## Scientific papers

Count a paper only when its full text is available and relevant to the research question, the source identifies a scholarly publication venue, and the paper is peer-reviewed. Record title, authors, venue, year, digital object identifier when present, publisher or repository, review evidence, direct full-text URL, access basis, local filename and relevant pages. A preprint may be useful background but does not count unless peer review is independently established. Abstract-only records, theses, slide decks, patents and vendor white papers do not count as scientific papers for this threshold.

Deduplicate by digital object identifier, then normalized title/authors/venue. Treat a preprint and its published version as one work. Keep a note of the relation and count the full text with the strongest review evidence once.

## Reputation and relevance rubric

For each candidate, assess separately:

1. **Authority:** responsible manufacturer, standards body, peer-reviewed venue, recognized scholarly publisher, or named author/institution with verifiable credentials.
2. **Relevance:** directly addresses the target feature, architecture, implementation or application question.
3. **Currency:** revision/publication date relative to the current design generation and applicable standard.
4. **Evidence quality:** concrete technical details, measurements, methods, citations and limitations rather than unsupported claims.
5. **Independence:** whether the source is independent of other selected sources or repeats vendor claims.

Use a simple qualitative level (high, medium, low) with a sentence of rationale. Citation counts may be supporting context only; never use them as the sole quality or truth criterion.

## Search and legal access

Search manufacturer and standards-body pages for product documents; use scholarly indexes, publisher pages, institutional repositories and author repositories for papers. Log exact queries and date. Prefer canonical publisher copies or lawful open versions. Confirm that a repository states a license or open-access basis before labeling a paper open access. A publicly reachable document may still carry restrictions; preserve its notice and do not redistribute it.

If full text is unavailable without credentials, do not bypass the access control. Ask the user to supply an authorized copy if they have access. Do not count an abstract or metadata record toward the full-text threshold. Keep standards specifications separate from scholarly papers and product datasheets.

## Minimum threshold audit

Before describing the study as complete, confirm at least ten distinct, locally retained product-family documents and ten distinct, locally retained, full-text peer-reviewed papers. Confirm relevance and quality manually; the manifest checker verifies only metadata shape, keys, file presence and hashes. If either set is short, issue an `INCOMPLETE` status and state the exact shortfall.
