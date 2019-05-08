import wikipediaapi
english = 'en'


class WikiExtractor(object):
    """Fetches content from wikipedia using APIs

    """

    def __init__(self, language=english):
        self.language = language
        self.wikipedia = wikipediaapi.Wikipedia(self.language)

    def get_section_content(self, page_title, section_title):
        page = self.wikipedia.page(page_title)
        section = page.section_by_title(section_title)

        return section.text

    def get_sections(self, sections, num_levels=None, sub_level=0):
        section_titles = []

        if num_levels is None:
            levels = sub_level + 1
        else:
            levels = num_levels

        for s in sections:
            if levels == sub_level:
                section_titles.append(s.title)
            else:
                section = dict()
                if len(s.sections) > 0:
                    if num_levels is not None:
                        sub_sections = self.get_sections(s.sections, levels, sub_level + 1)
                    else:
                        sub_sections = self.get_sections(s.sections, num_levels)
                    section[s.title] = sub_sections
                    section_titles.append(section)
                else:
                    section_titles.append(s.title)

        return section_titles
