import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

def generate_pdf():
    # 1. შრიფტის რეგისტრაცია
    font_path = "C:\\Windows\\Fonts\\sylfaen.ttf"
    if not os.path.exists(font_path):
        font_path = "sylfaen.ttf"
    pdfmetrics.registerFont(TTFont('Sylfaen', font_path))
    
    pdf_filename = "C:\\Users\\Utente\\Desktop\\travelgo\\TravelGo_Backend_Presentation.pdf"
    
    # დოკუმენტის ზომები და მარჟინები
    doc = SimpleDocTemplate(
        pdf_filename, 
        pagesize=letter,
        rightMargin=45, 
        leftMargin=45, 
        topMargin=40, 
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # 2. დიზაინის სტილები
    title_style = ParagraphStyle(
        'GeorgianTitle',
        parent=styles['Heading1'],
        fontName='Sylfaen',
        fontSize=20,
        leading=26,
        textColor=colors.HexColor('#006749'),
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'GeorgianSubtitle',
        parent=styles['Heading2'],
        fontName='Sylfaen',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#006749'),
        spaceBefore=14,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'GeorgianBody',
        parent=styles['BodyText'],
        fontName='Sylfaen',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6
    )
    
    card_text_style = ParagraphStyle(
        'CardText',
        parent=body_style,
        fontName='Sylfaen',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#2c3e50')
    )
    
    story = []
    
    # ━━━ PAGE 1: TITLE & ACCESS ━━━
    story.append(Paragraph("<font name='Helvetica-Bold' size='10' color='#7f8c8d'>TravelGo Backend Engine v1.0</font>", body_style))
    story.append(Paragraph("TravelGo ბექენდ ძრავის და მართვის სისტემის პრეზენტაცია", title_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph("მოგესალმებით! ეს არის TravelGo პროექტის ცენტრალური სერვერული სისტემის (Backend) და ადმინისტრაციული მართვის პანელის სრული აღწერილობა. სისტემა წარმატებით არის აწყობილი, ტესტირებული და გაშვებული ონლაინ რეჟიმში. ქვემოთ მოცემულია პირდაპირი ბმულები და ავტორიზაციის მონაცემები სატესტო რეჟიმში დასათვალიერებლად.", body_style))
    story.append(Spacer(1, 8))
    
    # წვდომების ბარათი
    card_data = [
        [Paragraph("<b>წვდომის ბმულები და ავტორიზაცია:</b>", card_text_style)],
        [Paragraph("ადმინ პანელი (მართვის პულტი): <font name='Helvetica' color='#2980b9'><a href='https://travelgo12.pythonanywhere.com/admin/'>https://travelgo12.pythonanywhere.com/admin/</a></font>", card_text_style)],
        [Paragraph("მომხმარებელი და პაროლი: <font name='Helvetica-Bold'>ganza.core@gmail.com / admin123</font>", card_text_style)],
        [Paragraph("Swagger API (ინტერაქტიული დოკუმენტაცია): <font name='Helvetica' color='#2980b9'><a href='https://travelgo12.pythonanywhere.com/swagger/'>https://travelgo12.pythonanywhere.com/swagger/</a></font>", card_text_style)]
    ]
    
    card_table = Table(card_data, colWidths=[doc.width])
    card_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#006749')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(card_table)
    story.append(Spacer(1, 10))
    
    # ━━━ SWAGGER SECTION ━━━
    story.append(Paragraph("რა არის სვაგერი (Swagger UI) და რატომ არის ის მნიშვნელოვანი?", subtitle_style))
    story.append(Paragraph("სვაგერი არის ინტერაქტიული ხიდი ჩვენს სერვერსა და მობილურ აპლიკაციას (Flutter) შორის. როდესაც მობილური აპლიკაციის დეველოპერი იწყებს მუშაობას, მას სჭირდება ზუსტად იცოდეს, თუ რა ფორმატში უნდა გაუგზავნოს მონაცემები სერვერს და რას მიიღებს პასუხად. სვაგერი ავტომატურად აგენერირებს ამ დოკუმენტაციას კოდიდან და დეველოპერს აძლევს საშუალებას პირდაპირ ბრაუზერიდან გატესტოს ნებისმიერი მოთხოვნა (მაგალითად, გაგზავნოს GPS კოორდინატები და ნახოს, ჩაეთვლება თუ არა ჩექინი მომხმარებელს). ეს გამორიცხავს გაუგებრობებს და პროგრამისტებს შორის კომუნიკაციის დროს მინიმუმამდე ამცირებს.", body_style))
    
    # ━━━ GENERAL WORKINGS ━━━
    story.append(Paragraph("ადმინ პანელის მუშაობის ზოგადი პრინციპი:", subtitle_style))
    story.append(Paragraph("ადმინ პანელი აგებულია როლურ პრინციპზე. ადმინისტრატორს აქვს სრული კონტროლი მონაცემებზე. მას შეუძლია მართოს მომხმარებლები, პარტნიორი ობიექტები (რესტორნები, სასტუმროები, მუზეუმები) და მათი ფასდაკლების კუპონები. რაც მთავარია, სისტემა მხარს უჭერს სრულ ორენოვნებას (ქართულ და ინგლისურ ენებს) - ადმინ პანელში შეყვანილი ნებისმიერი ინფორმაცია მობილურ აპლიკაციაში აისახება იმ ენაზე, რომელიც მომხმარებელს აქვს არჩეული ტელეფონში.", body_style))
    
    story.append(PageBreak()) # გადავიდეთ მეორე გვერდზე
    
    # ━━━ PAGE 2: DETAILED MODULES ━━━
    story.append(Paragraph("ბექენდის ფუნქციონალური მოდულების დეტალური განხილვა:", title_style))
    story.append(Spacer(1, 5))
    
    modules = [
        ("ავტორიზაცია და მომხმარებლები (users)", 
         "მხარს უჭერს უსაფრთხო JWT ტოკენებზე დაფუძნებულ რეგისტრაციას და ავტორიზაციას. ინახავს მომხმარებლის პროფილის მონაცემებს (ფოტო, ქვეყანა, ქალაქი, ინტერესები, მოგზაურის ტიპი) და გეიმიფიკაციის სტატისტიკას (XP, დონეები, ქოინები). იქვე მუშაობს რეფერალური სისტემა, რომელიც თითოეულ იუზერს ანიჭებს უნიკალურ 6-ნიშნა კოდს მეგობრების მოსაწვევად და ბონუს ქულების მისაღებად."),
         
        ("ინტერაქტიული რუკა და ჩექინები (maps)", 
         "მართავს რუკაზე არსებულ წერტილებს (POI - Points of Interest). თითოეულ წერტილს აქვს კოორდინატები, ორენოვანი აღწერა, ფოტოები, სამუშაო საათები და აუდიო გიდის ფაილები. ჩექინის გაკეთებისას მუშაობს Anti-Cheat ლოგიკა, რომელიც ამოწმებს, იმყოფება თუ არა მომხმარებელი რეალურად ამ ლოკაციის რადიუსში (მაგ. 100 მეტრში) და მხოლოდ ამის შემდეგ აჯილდოებს მას შესაბამისი XP-ით ან ბეჯით."),
         
        ("Anti-Scam წითელი ზონები (Red Zones)", 
         "უსაფრთხოების მოდული, რომელიც ადმინისტრატორს საშუალებას აძლევს რუკაზე მონიშნოს მაღალი საფრთხის შემცველი რეგიონები ან ადგილები გარკვეული რადიუსით. მობილური აპლიკაცია ამ კოორდინატებს იღებს API-დან და მომხმარებლის ამ ზონაში შესვლისას აჩვენებს სპეციალურ გაფრთხილებას."),
         
        ("პარტნიორები და კუპონები (partners)", 
         "ბიზნეს პარტნიორების მართვა (ლოგოები, კატეგორიები, ფასდაკლების პროცენტები). მომხმარებლის მიერ ჩექინის წარმატებით შესრულების შემდეგ, სისტემა ავტომატურად აგენერირებს ფასდაკლების კოდს/კუპონს, რომლის გამოყენებაც პარტნიორ ობიექტებშია შესაძლებელი. ადმინ პანელიდან ხდება კუპონების ვალიდურობის და სტატუსების კონტროლი."),
         
        ("ყოველდღიური დავალებები (quests)", 
         "გეიმიფიკაციის ნაწილი, სადაც იქმნება ყოველდღიური ქუესტები (დავალებები კონკრეტული ლოკაციების მონახულებაზე). ადმინს შეუძლია განსაზღვროს დავალების აქტიურობის თარიღი, საჭირო ჩექინების რაოდენობა და ჯილდო (XP და ქოინები). აქვე აღირიცხება მომხმარებლების ინდივიდუალური პროგრესი."),
         
        ("Rewards მაღაზია და ინვენტარი (inventory)", 
         "მაღაზია, სადაც მოგზაურები დაგროვებული ქოინებით ყიდულობენ სპეციალურ ნივთებს: ბეჯებს და ავატარის სკინებს. ადმინს აქვს სრული კონტროლი ნივთების ფასებზე, შეუძლია ნივთი მონიშნოს როგორც 'გაყიდვაშია' ან დროებით ამოიღოს მაღაზიიდან, ასევე ნახოს ვის რა ნივთი აქვს განბლოკილი."),
         
        ("სოციალური ქსელი და გამოწვევები (social)", 
         "უზრუნველყოფს მეგობრობის სისტემას (მოთხოვნის გაგზავნა, დადასტურება, დაბლოკვა). მოიცავს სოციალურ Feed-ს, სადაც მომხმარებლები ხედავენ მეგობრების აქტივობებს (ახალი დონე, მიღებული ბეჯი, ჩექინი). ასევე მუშაობს 'Challenge' მოდული, რომლითაც მეგობრები ერთმანეთს იწვევენ ლოკაციებზე ბონუს XP-ის სანაცვლოდ."),
         
        ("გლობალური პარამეტრები (configuration)", 
         "ცალკე გამოყოფილი მოდული გლობალური ცვლადებისთვის, როგორიცაა: ჩექინის მაქსიმალური რადიუსი, რეფერალური ბონუსები, აპლიკაციის ტექნიკური შესვენების რეჟიმი (Maintenance Mode) და მინიმალური ვერსიის კონტროლი. ასევე აქედან იმართება Onboarding სლაიდები და AR კამერის ტუტორიალის ნაბიჯები.")
    ]
    
    table_data = []
    for title, desc in modules:
        table_data.append([
            Paragraph(f"<b>{title}</b>", card_text_style),
            Paragraph(desc, body_style)
        ])
        
    modules_table = Table(table_data, colWidths=[160, doc.width - 160])
    modules_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(modules_table)
    story.append(Spacer(1, 10))
    
    # ━━━ TECHNICAL STACK ━━━
    story.append(Paragraph("ტექნოლოგიური სამუშაო სტეკი:", subtitle_style))
    stack_desc = (
        "პროექტი აგებულია <b>Python 3.10</b> და <b>Django 6.0</b> ფრეიმვორკით. "
        "მობილურ აპლიკაციასთან კავშირისთვის გამოიყენება <b>Django REST Framework (DRF)</b>. "
        "API დოკუმენტაცია ავტომატურად იწყობა <b>drf-yasg (OpenAPI 3.0)</b>-ით, "
        "ხოლო ონლაინ ჰოსტინგად გამოყენებულია <b>PythonAnywhere</b>."
    )
    story.append(Paragraph(stack_desc, body_style))
    
    # დოკუმენტის აშენება
    doc.build(story)
    print("Beautiful expanded PDF generated successfully at Desktop/travelgo!")

if __name__ == "__main__":
    generate_pdf()
