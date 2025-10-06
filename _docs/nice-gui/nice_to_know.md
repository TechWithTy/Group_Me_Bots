Test

I decided to recreate this page. The style of that page always frustrated me. Pure white, walls of text, no differentiation. Government organization with outdated tools, what can you do? It's mostly a static page, but shows off nicegui's abilities for modern design.

Screenshots at end of post. Here are thumbnails of my page:

thumbnail-seq
thumbnail-news

My background: decades of experience as a dabbler in web development. It's not my main role since early in my career, but is a part of what I do. Created many pages with manual html and css, several browser extensions, and a few python web apps from scratch (no frameworks). Developed a few sites with perl and php early in my career. Recently tried a bit of mako and jinja for page generation. Never used flask, tailwind, quasar, or any other python or js frameworks.
Things that were easy to do with nicegui:

    dark mode
    tabs for middle part (applicants, offices)
    timeline for news items
    expandable text
    icons for more visual appeal
    download buttons with notification popup

Things that should have been easy but were difficult to figure out from nicegui docs:

    setting widths on things (images, tabs, etc)
    making headers, meaning actual <h[1-6]> tags. the only text element available is ui.label, which is neither a header nor a paragraph, but a div. creating actual headers and <p> text would be nice without resorting to ui.element. Maybe ui.para and ui.h1, ui.h2, ...?
    nesting arbitrary html elements (finally found buried in the docs that any element can be nested using with).
    alignment. getting an image to sit on the right took a lot of trial and error. I know how to do it manually with css, but with nicegui layout options it wasn't clear at all. I could do columns or a grid, but I wanted content to flow around the image. Finally found tailwind float-right, but had trouble figuring out how to compose the elements for it to work. Ended up wrapping image and text in a generic ui.element ('div')
    spacing. by default buttons are touching, which is awful for usability. adding clear separation between adjacent buttons was hard to figure out. likewise the default spacing has headers touching body text with no separation above or below. really bad for readability.
    setting global style defaults, like font sizes, link colors, etc. eventually I just gave up and manually inserted a <style> tag in the page header. couldn't find any docs on how to set global styles.
    the difference between .props () and .classes () and .style (). Not clear at all which elements support which methods, or when to use which method. Eg should I set width with props ('width=50%') or with classes ('w-50')?
    surprisingly, the single hardest thing was setting the green color on download buttons. You'd think passing the color = flag to ui.button() would work, but no. Then you'd try ui.button().classes (color) but that doesn't work either. Finally I stumbled on the solution - you have to do both together! Very strange behavior.

Things I never figured out how to do:

    Change global font sizes. h1, h2, h3, h4 are all ridiculously huge by default, while normal text is hopelessly small. <h1> shouldn't be 5 times the size of <p>. h4 in nicegui is the size of h1 on most sites.
    Create an actual header. Everything is <div class="text-h4"> instead of a real <h4>. This makes the content very hard to parse, eg by search engines, web scrapers, and semantic tools.
    Add normal paragraph text. Is there a way other than raw ui.html or ui.element? Everything in ui.label turns into a <div>.
    calling run (dark = true) does nothing. had to call dark.enable () to start in dark mode.
    getting icons to line up with a text label. by default icons want to be on their own line. I fixed that - it was tricky, had to wrap both icon and label in a div - but couldn't figure out vertical alignment (icon still slightly higher than text). seems like a common use case, having icons next to a link or text.

Conclusion

nicegui is fantastic. Very powerful tools for creating complex elements with minimal code. I'm beyond impressed. My demo only scratches the surface of what nicegui can do, but the results are exceptional.

The one thing that can be improved is the docs. They're very good in some ways. The showcase page does a great job showing what elements are available and some basic options. But a number of general topics are missing, such as global styles, composing a complete page, making text elements other than ui.label, etc.

The reference pages make it hard to find key information. I had to resort to things like help (ui.element.style ()) in the python console to find out that multiple styles should be separated by ; instead of space, and error messages to tell me that the format is name:val, not name=val as with props ().
Suggestions to improve the docs

    don't assume experience with tailwind / quasar. expand the section on styling to show how to set different style elements: width, font, color, position, padding, margins, etc. the common things people need to do with web content.
    have a section on how to set global style values / defaults for the entire app. Fonts, spacing, colors, things like that.
    examples of composing a complete page with nested structure
    how to make text elements other than label
    differentiate the reference pages better. Eg the page for ui.icon has 10 flavors of bind_* methods to scroll through just to find the props method. Ref pages can be improved with 1) a clickable index of all function names at the top or side, so you can immediately jump to props if that's what you need, and 2) less repetition of common methods that every class has. Methods that many elements share can just link to the base class page, instead of cluttering up every ui.button, ui.icon, etc page with a dozen different bind_* methods.
    colored syntax highlighting on ref pages would make it easier to read. better differentiate code from explanatory text.

Sequence page

News section cut off for some reason
Screenshot_2023-10-09 WIPO Sequence
News items

Screenshot_2023-10-09 WIPO Sequence news
Replies: 6 comments · 4 replies

ed2050
on Oct 9, 2023
Author

Here's my code if anyone wants to see how I did things.

import os

from nicegui import ui

true, false, none = True, False, None

# ---------------------------------------------

WIPO_STYLES = '''
<style>
body {
	font-size : 20px ;
}
img[src$="pdf.svg"] ,
img[src$="zip.svg"] {
    background-image: initial;
    background-color: rgb(0, 77, 169);
	display : inline-block ;
    background: #0067B8;
    padding: 3px;
    max-height: 16px;
    /* vertical-align: text-bottom; */
    margin: 0 4px;
}

a {
    color: #0059C6 !important;
}

p
{
	margin-bottom : 1em !important ;
}

h1, h2, h3, h4, h5, h6 ,
/* .text-h1, .text-h2, .text-h3, */
.text-h4, .text-h5, .text-h6
{
	margin-top : 1em !important ;
	margin-bottom : 0.5em !important ;
}
</style>
'''

# ---------------------------------------------

async def alert () :
	await ui.run_javascript ('alert("Hello!")', respond = false)

# ---------------------------------------------

ISDARK = true

#@ui.page ('/')
def mainpage () :

	ui.add_head_html (WIPO_STYLES)

	# adding wipo stylesheets breaks the page
	#ui.add_head_html ('<link rel="https://www.wipo.int/stylesheet" href="https://www.wipo.int/export/system/modules/org.wipo.internet.rwd.templates/resources/css/styles2016.css">')
	#ui.add_head_html ('<link rel="https://www.wipo.int/stylesheet" href="https://www.wipo.int/export/system/modules/org.wipo.internet.rwd.templates/resources/css/styles2016-universal.css">')
	#ui.add_head_html ('<link rel="https://www.wipo.int/stylesheet" href="https://www.wipo.int/export/system/modules/org.wipo.internet.rwd.templates/resources/webfonts/ss-standard.css">')


	dark = ui.dark_mode ()

	# -----

	with ui.left_drawer (top_corner = true, bottom_corner = true).style ('background-color: #33c'):

		switch = ui.switch ('Dark mode', value = ISDARK, on_change = dark.toggle)

		#ui.label ('Switch mode:')
		#ui.button ('Dark', on_click = dark.enable)
		#ui.button ('Light', on_click = dark.disable)

	# -----

	ui.label ('WIPO Sequence').classes ('text-h3')

	with ui.element ('div').classes ('') :
		ui.image ('https://www.wipo.int/export/sites/www/standards/images/wipo-sequence-845.jpg').props ('width=25vw').style ('margin-bottom:2em; margin-left:3em').classes ('float-right')

		ui.html ('''
<p>WIPO Sequence is a global software tool that enables patent applicants to prepare amino acid and nucleotide sequence listings compliant with <a href="https://www.wipo.int//export/sites/www/standards/en/pdf/03-26-01.pdf" rel="https://www.wipo.int/noopener">WIPO Standard ST.26 <img src="https://www.wipo.int//export/sites/www/shared/images/icon/new/pdf.svg" alt="PDF, WIPO Standard ST.26"></a> as part of a national or international patent application.</p>

<p class="lead">WIPO Sequence Validator is a web service for patent offices to verify that filed sequence listings comply with WIPO ST.26.</p>

<p>These tools were developed in collaboration with patent offices around the world, under the direction of the <a href="https://www.wipo.int//cws/en/">Committee on WIPO Standards</a>.</p>

<div class="alert alert--warning">
<p><strong>Note</strong>: WIPO Standard ST.26 is now in force.</p>
<p>WIPO Sequence Suite version 2.3.0 was released on 2023.05.08</p>
</div>
		''')

	ui.separator ()

	# -----

	with ui.tabs ().classes ('w-full') as tabs :
		tabapp = ui.tab ('For Applicants')
		taboff = ui.tab ('For Patent Offices')

	with ui.tab_panels (tabs, value = tabapp).classes ('w-50') :

		with ui.tab_panel (tabapp) :

			ui.label ('WIPO Sequence Suite').classes ('text-h4')

			ui.html ('''
<p>A standalone desktop application available for Windows, Linux and MacOS. A <a href="https://www.wipo.int/export/sites/www/standards/en/sequence/wipo-sequence-manual.pdf">User Manual <img src="https://www.wipo.int/export/sites/www/shared/images/icon/new/pdf.svg" alt="PDF, WIPO Sequence version 1.1.0 User Manual"></a> is provided to assist applicants with generating compliant sequence listings.</p>
			''')

			with ui.card ().classes ('bg-stone-200 dark:bg-stone-700 w-50 float-right') :
				
				with ui.element ('div').classes ('text-h6 w-full') :
					ui.icon ('help').classes ('float-left')
					ui.label ('Need help?')

				ui.html ('''
<p>Visit the Knowledge Base for help with WIPO Sequence.</p>
<p>This includes known issues and how to report bugs.</p>
				''')

				ui.button (
					'Knowledge Base',
					icon = 'rocket' ,
					on_click = 'https://www3.wipo.int/confluence/x/EwAxRg' ,
				).classes ('bg-blue-700')

			ui.label ('Download').classes ('text-h6')
			ui.html ( '''
<p>By downloading and installing WIPO Sequence, you are accepting the following <a href="https://www.wipo.int/export/sites/www/standards/en/sequence/wipo-sequence-terms-use-en.pdf">Terms of Use (October 2021) </a>.</p>
			''')

			# ---

			ui.label ('Select your platform...')

			def startdl (link) :
				ui.download (link)
				ui.notify('Your download has started', type = 'positive')

			dlwin = 'https://wiposequence.wipo.int/download/wiposequence/win/WIPO+Sequence+Setup+2.3.0.exe'
			dlmac = 'https://wiposequence.wipo.int/download/wiposequence/osx/WIPO Sequence-2.3.0.dmg'
			dlnix = 'https://wiposequence.wipo.int/download/wiposequence/linux/WIPO%20Sequence%202.3.0.AppImage'

			dlc = 'bg-green-400 dark:bg-green-600'
			cls = dlc + ' block m-4'

			ui.button ('Mac OS' , icon = 'favorite' , on_click = lambda : startdl (dlmac), color = dlc).classes (cls)
			ui.button ('Linux'  , icon = 'plumbing' , on_click = lambda : startdl (dlnix), color = dlc).classes (cls)
			ui.button ('Windows', icon = 'delete' , on_click = lambda : startdl (dlwin), color = dlc).classes (cls)

			# ---

			ui.label ('Updates').classes ('text-h6')
			ui.html ('''
<p>Sign up for the mailing list to receive notifications of software updates and related issues: <a id="signup" href="/standards/en/sequence/signup.html">WIPO Sequence Updates</a></p>
			''')

			ui.label ('Test data set — ST.26 DTD version 1.3').classes ('text-h6')
			ui.html ('''
<p>The following ZIP file provides both compliant and non-compliant ST.26 instances for testing purposes: Test data set <a href="https://www.wipo.int/standards/en/sequence/valid_and_error.zip"><img src="https://www.wipo.int/export/sites/www/shared/images/icon/new/zip.svg" alt="ZIP, Test data set ST.26 DTD version 1.3"></a></p>
			''')

		# ---

		with ui.tab_panel (taboff) :

			ui.label ('WIPO Sequence Validator').classes ('text-h4')

			ui.html ('''
<p>A web service that runs in patent office environments to check filed sequence listings for compliance with WIPO Standard ST.26. Patent Offices may obtain WIPO Sequence Validator by <a href="mailto:wiposequence@wipo.int">contacting us</a>.</p>
<h3>Validator Materials</h3>
<ul>
<li><a href="/export/sites/www/standards/en/sequence/wipo-sequence-validator-terms-use-en.pdf" rel="noopener">WIPO Sequence Validator Terms of Use <img src="https://www.wipo.int/export/sites/www/shared/images/icon/new/pdf.svg" alt="PDF, WIPO Sequence Validator Terms of Use"></a></li>
<li><a href="/export/sites/www/standards/en/sequence/wipo-sequence-validator-manual-2-3-0.pdf">WIPO Sequence Validator Operations Manual <img src="https://www.wipo.int/export/sites/www/shared/images/icon/new/pdf.svg" alt="PDF, WIPO Sequence Validator version 1.1.0 Operations Manual"></a></li>
</ul>
			''')

			ui.separator()

	# -----

	ui.label ('News').classes ('text-h4') 

	with ui.timeline (side = 'right') :
		
		ui.timeline_entry (
			'' ,
			title    = 'Version 2.2.0 of WIPO Sequence Suite released for general use' ,
			subtitle = 'Oct 2022' ,
			icon     = 'rocket_launch' ,
		)

		with ui.timeline_entry (
			'' ,
			title    = 'WIPO Standard ST.26 goes live' ,
			subtitle = 'July 2022' ,
			icon     = 'biotech' ,
		) :
			
			ui.link ('Full story ', 'https://www.wipo.int/pct/en/news/2022/news_0039.html', new_tab = true)
			ui.icon ('launch')

		with ui.timeline_entry (
			'' ,
			title    = 'Version 2.1 of WIPO Sequence Suite released ' ,
			subtitle = 'June 2022' ,
			icon     = 'public' ,
		) :
			with ui.expansion ('Show more', icon = 'swap_vert').classes ('w-full') :
				ui.html ('''
<p>After releasing WIPO Sequence Suite version 2.0 in May, WIPO has continued resolving known issues to ensure the software is production ready for the WIPO ST.26 implementation date of July 1. Improvements in version 2.1 include upgrading the “Help” features and refining import messages. Changes since version 2.0.0 are summarized in the Release Notes on the <a href="https://www.wipo.int/standards/en/sequence/index.html">WIPO Sequence home page</a>.</p>
<p>If you do not receive the auto-update message in WIPO Sequence Suite, please download version 2.1.0 using the links above.</p>
				''')

		with ui.timeline_entry (
			'' ,
			title    = 'Next stable release of WIPO Sequence; Knowledge Base & email list' ,
			subtitle = 'May 2022' ,
			icon     = 'model_training' ,
		) :

			with ui.expansion ('Show more', icon = 'swap_vert').classes ('w-full') :
				ui.html ('''
<p>Based on the feedback of our testing group, WIPO has continued to improve the WIPO Sequence Suite to ensure that it meets the needs of users for the July 1 WIPO ST.26 implementation date. The result will be WIPO Sequence version 2.0.0, scheduled for release in the week of May 16. Improvements since the last stable version will be summarized in the Version 2.0.0 Release Notes to be provided in the Download section.</p>
<p>To help support users, WIPO is also collaborating with patent Offices to produce a <a href="https://www3.wipo.int/confluence/x/EwAxRg">knowledge base</a> of answers to regularly asked questions and common issues. This knowledge base will be available to the public from June 1.</p>
<p>WIPO Sequence users are encouraged to sign-up to the new <a href="/standards/en/sequence/signup.html">email list</a> for important announcements and information on software updates and related issues. Users will be prompted to register for the list when downloading the software from the WIPO Sequence homepage. </p>
</article>
				''')

		with ui.timeline_entry (
			'' ,
			title    = 'Second stable release of WIPO Sequence' ,
			subtitle = 'Oct 2021' ,
			icon     = 'build' ,
		) :

			with ui.expansion ('Show more', icon = 'swap_vert').classes ('w-full') :
				ui.html ('''
<p>Since November 2021, WIPO has been developing an improved version of the WIPO Sequence Suite. The latest version of the desktop tool can be downloaded above along with the release notes which indicate the changes since the last stable release was published. Patent Offices interested in the latest version of WIPO Sequence Validator should <a href="mailto:wiposequence@wipo.int">contact us</a>.</p>
				''')

		with ui.timeline_entry (
			'' ,
			title    = 'WIPO ST.26 Training Webinar Series' ,
			subtitle = 'April 2021' ,
			icon     = 'ondemand_video' ,
		) :
			
			with ui.expansion ('Show more', icon = 'swap_vert').classes ('w-full') :
				ui.html ('''
<p>WIPO is providing four webinars on preparing sequence listings compliant with WIPO Standard ST.26. The webinars are open to patent applicants and IP Offices. See the <a href="https://www.wipo.int/meetings/en/topic.jsp?group_id=330">webinars page</a> for dates in April and May and other information. Recordings will be available.</p>
				''')

	ui.separator()
	
	title = 'WIPO Sequence'

	if ISDARK :
		dark.enable ()

	ui.run (
		title = title ,
#		dark = true ,  # doesnt work
#		port = native_mode.find_open_port () ,
#		reload = false,
	)

# ---------------------------------------------

if __name__ in { '__main__', '__mp_main__' } :
	mainpage ()

0 replies
stdusr
on Oct 9, 2023

I’m experiencing similar issues. Although NiceGUI is a fantastic tool, styling, positioning, and layout can be a bit of a headache for coders without much experience in web development. Your code will be a good reference. Thank you for your effort!
0 replies
rodja
on Oct 9, 2023
Maintainer

@stdusr Thank you so much for taking the time to write it all down. You have a lot valuable points. For some we already have separate feature requests. We'll need to go over this list in the next days and extract other points to implement or further discuss in separate topics.
1 reply
@ed2050
ed2050
on Oct 10, 2023
Author

One thing I'm considering is how to better separate functionality from style. I dislike littering my code with style elements like .classes ('w-50') or classes ('bg-blue-200'). It makes styles hard to change later, and it makes the code harder to follow. I like styles to be centralized, not scattered throughout.

Does anyone have suggestions how to accomplish this? My thoughts so far:

    One approach could be using variables like buttoncolor = 'bg-blue-200' to have a single source. It helps a bit, but still has code littered with .classes (bgcolor) calls. I want more separation.

    Ideally I could use a declarative language like css. Then it's easy to make all buttons blue, or make the first button green, etc. The problem is I don't want to do low level css styling. Tailwind and quasar provide nice response layouts that take care of all the little gotchas with css. Can I leverage that by just applying their built-in classes like w-50 in my own css file? Maybe. I'll have to look at the Tailwind reusability page in more depth.

    But also, many tailwind classes don't work. For instance, make a ui.card ().classes ('w-50'). This should make the card width 50% but it doesn't. The card is full width of parent container. I haven't figured out yet which classes work in which circumstances.

    If declaring my own css doesn't work for whatever reason, I could also live with python code that adds styling separately from the functional declarations. Eg something like this:

def add_nodes (root) :
    with root :
        ui.label ('Are you ready?')
        ui.button ('Let's go!')
    return root

def add_styles (root) :
    for label in root.labels () :   # return all labels under root?
        label.classes ('bg-blue-200')

   for button in root.buttons () :   # return all button under root?
       button.classes ('w-25 bg-green-500')
    return root

def main () :
    root = ui.column ()
    add_nodes (root)
    add_styles (root)

    What would help with this approach is a way to select certain items under root. Could be by tag, by class, by id, etc. Something like BeautifulSoup's find_all method, or even better css.select that returns all nodes matching an arbitrary css selector. Something like root.select ('button.myclass') would be useful. Does nicegui have anything like that?

    along these lines, I'm suprised you can pass classes, colors, icons to many element constructors but not an id parameter. What's the proper way to set an id on a nicegui element? Say I want a certain card to have <div class="q-card..." id="foo">. Would it be props, as in ui.card ().props ('id=foo')?

0 replies
ed2050
on Oct 11, 2023
Author
Update on CSS Method

Well the css method appears to have limitations. It works for some things (font sizes, colors, margins) but doesn't work for others (positioning).

Here's a short example. Tried to make a card with an icon and a label side by side on one line.

from nicegui import ui
true, false, none = True, False, None

STYLES = '''
h1, h2, h3, h4, h5, h6  {  font-weight : bold ;  }
.q-card  {  width : 50% ;  }
.q-card i   {  font-size : 2rem ;    display : inline-block ;  }
.q-card .text   {    display : inline-block ;    }   
'''

# put custom styles as the first element on the page.
# cant put in <head> with ui.add_head_html because tailwind.css comes later and overrides
ui.html (f'<style> { STYLES } </style>')

with ui.card () :
    ui.icon ('settings_input_hdmi')
    ui.label ('NO NAME').classes ('text')

    # also tried making para as: ui.html (f'<p> NO NAME </p>')
    # doesn't work, nicegui wraps the para in a div element 🙄

Result in chrome looks like this:
Screen Shot 2023-10-11 at 12 16 06 PM

Chrome dev console shows that inline-block is applied to both elements: the icon (which is an <i> tag) and the text (which is <div class="text">). But for some reason they still don't display inline. Result is the same if you change inline-block to inline.

I tried flex and other display styles too. Nothing changes the result. Icon is always on its own line above the text element.
Takeaway

In normal css these techniques work fine. Something about tailwind or quasar must be altering how display works. Probably not worth fixing with pure css becase you'll have to delve into the depths of how tailwind / quasar do positioning, alter low-level css, and likely break the responsive layouts. Solution would be fragile and might break other things.
Controlling Width

One thing actually worked better in css. I couldn't control card width in nicegui. Neither .classes ('w-50') nor .props ('width=50%') works on ui.card. But the css line .q-card  {  width : 50% ;  } works perfectly. So there's a win for regular css.
2 replies
@falkoschindler
@ed2050
ed2050
on Oct 11, 2023
Author

Thanks falko. You're right, I confused w-50 with something else. There's w-5 and w-52 but not w-50.
Here's the list of Tailwind width properties.

I think I found the issue with card. Class nicegui-card uses flex-direction : column by default. That's why my inline-block stylings didn't work. The following fixes seem to work, with slightly different spacing in results:

    adding ui.row () between ui.card and contents
    setting .style ('flex-direction : row') on ui.card
    adding .nicegui-card { flex-direction : row; } to stylesheet

Of these I like #3 the best for cleaner code. It has global effect, but can be tailored to specific parts of the page if needed. We'll see how it goes.

Thanks for your help. Hope I'm not flooding the board. Just trying to capture what I learn.
falkoschindler
on Oct 13, 2023
Maintainer

Thanks for sharing your impressions in such detail, @ed2050! I won't be able to address every single point in this thread, but let me share my thoughts, mainly about your suggested improvements:

    don't assume experience with tailwind / quasar
    I totally agree. We already try to make NiceGUI approachable for non-web-developers. But it's hard to find the right measure between explaining HTML, CSS, Tailwind and Quasar in our docs or referring to their documentations. You can always write more, but it doesn't mean it will be found and read.
    For example, you say the right separator for styles ";" was hard to find. But the very section about styling shows it in the demo code.

    have a section on how to set global style values / defaults for the entire app
    Just recently we introduced default classes, props and style (see e.g. https://nicegui.io/documentation/element#default_style). But sure, we might add a paragraph about it in the styling section.

    how to make text elements other than label
    We decided not to add elements like ui.p or ui.h1, since these are names from the HTML world and we focussed on building a UI framework, not necessarily targeted at web apps. And we didn't want to assume the user to know HTML (see point 1). But I see your point: If you want to build serious web apps, you look for more nuanced elements than ui.label.

    differentiate the reference pages better, a clickable index, less repetition of common methods
    That's a valid point. Although I'm not sure how to separate "common methods" from others. If you only show the "own" methods of a class, the reference might be empty for some elements like ui.textarea, making methods and properties hardly discoverable. Note that most of the documentation is automatically generated from docstrings and code inspection. Therefore we'd need a rule which can be implemented.

    colored syntax highlighting on ref pages
    Yes, that might help. But the overall look of the page should not get too cluttered by introducing more colors.

Oh and one last thing: ui.run(..., dark=True) should definitely work. If it doesn't, we should debug and fix it.

To conclude: I second your suggestions, even though the concrete realization might be challenging. However, I'd suggest to discuss individual points in separate tickets, since this one is already getting pretty long. Or, even better, if you have specific suggestion on how to improve the documentation, a pull request is always very welcome (and forces us to take action). 🙂
1 reply
@ed2050
