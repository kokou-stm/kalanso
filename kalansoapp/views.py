from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404

from django.http import JsonResponse, HttpResponseForbidden
from .models import *

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.db.models import Q
from django.core.mail import EmailMessage
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.exceptions import ValidationError
import codecs, math
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl

from langchain_openai import AzureChatOpenAI
# Azure LLM config
llm = AzureChatOpenAI(
    openai_api_version="2024-07-01-preview",
    deployment_name="gpt-35-turbo-chefquiz",
    openai_api_key=settings.AZURE_OPENAI_API_KEY,
    openai_api_type="azure",
    azure_endpoint="https://realtimekokou.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2024-08-01-preview",
)


# from langchain.prompts import PromptTemplate
# from langchain.chains import RetrievalQA,  ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory
# from langchain_community.vectorstores import FAISS
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.memory import ConversationBufferMemory
# from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from django.contrib.auth.models import Group, Permission

# prof_group, created = Group.objects.get_or_create(name='Professeur')
# student_group, created = Group.objects.get_or_create(name='Etudiant')


email_address = settings.EMAIL_HOST_USER
email_password = settings.EMAIL_HOST_PASSWORD

smtp_address = settings.EMAIL_HOST
smtp_port = 465


@login_required
def upload_cours(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        file = request.FILES.get('file')

        # Validation simple des champs
        if not title or not description or not file:
            return render(request, 'upload_cours.html', {'error': 'Tous les champs sont obligatoires.'})
        #prof = Professeur.objects.get(username = request.user)
        # Sauvegarder les données dans le modèle
        course = Cours(title=title, description=description, file=file, author = request.user)
        course.save()
        save_path  = f"{course.id}"
        folder_path = os.path.join(settings.MEDIA_ROOT, save_path)
        print("folderpath: ", folder_path)
        cours_path = course.file.url
        
        #save_db(cours_path, folder_path, embeddings, course_id=f"{course.id}")
        #process_message_with_rag(cours)
        messages.info(request, f"{title} a été bien ajouté.")
        redirect_url = reverse('quiz_creator', args=[course.id])
        return JsonResponse({'redirect_url': redirect_url})
        
        #return redirect('quiz_creator', course_id=course.id)

    return render(request, 'upload_cours.html')



@login_required(login_url='login')
def home(request):
    indentifiant = str(request.user.username)[:2]
    context={"identifiant": indentifiant}
    if request.user.groups.filter(name='Professeur').exists():
        context['status'] = "Professeur"
    else:
        context['status'] = "Etudiant"
    return render(request, template_name="home.html", context=context)

# Create your views here.

@login_required(login_url='login')
def user_dashboard(request):

    user = request.user
    # profile = Profile.objects.get(user=user)
    context = {
        'user': user,
        
        'is_staff': user.is_staff,
    }
    return render(request, 'student_dashboard.html', context)
    




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils.pdf_utils import load_pdf_documents
from .utils.rag import create_vectorstore, rag_answer
import os

@csrf_exempt
def upload_pdf_view(request):
    if request.method == "POST" and request.FILES.get("file"):
        user_id = request.POST.get("user_id", "default_user")
        file = request.FILES["file"]
        filepath = f"media/{user_id}.pdf"
        persist_path = f"chroma/{user_id}"

        if os.path.exists(persist_path):
            return JsonResponse({"message": "Ce document a déjà été indexé."}, status=200)

        with open(filepath, "wb+") as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        documents = load_pdf_documents(filepath)
        create_vectorstore(documents, persist_path)
        return JsonResponse({"message": "Document indexé avec succès."}, status=201)

    return JsonResponse({"error": "Aucun fichier PDF fourni."}, status=400)


@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        question = data.get("question")
        user_id = data.get("user_id", "default_user")
        persist_path = f"chroma/{user_id}"

        if not os.path.exists(persist_path):
            return JsonResponse({"error": "Aucun document indexé pour cet utilisateur."}, status=404)

        answer = rag_answer(question, persist_path, llm)
        return JsonResponse({"response": answer})

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)






from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.conf import settings
import json
import os

@login_required
@require_http_methods(["GET"])
def list_modules(request):
    """Récupérer tous les modules de l'utilisateur"""
    try:
        modules = Module.objects.filter(auteur=request.user)
        modules_data = []
        
        for module in modules:
            modules_data.append({
                'id': module.id,
                'titre': module.titre,
                'description': module.description,
                'code': module.code,
                'domaine': module.domaine,
                'niveau': module.niveau,
                'date_creation': module.date_creation.isoformat(),
                'fichier_url': module.fichier.url if module.fichier else None,
                'fichier_nom': os.path.basename(module.fichier.name) if module.fichier else None
            })
        
        return JsonResponse({
            'success': True,
            'modules': modules_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def create_module(request):
    """Créer un nouveau module"""
    # try:
    titre = request.POST.get('titre')
    description = request.POST.get('description')
    code = request.POST.get('code')
    domaine = request.POST.get('domaine')
    niveau = request.POST.get('niveau')
    print(request.POST)
    # fichier = request.FILES.get('fichier')
    print(titre, description, code, domaine, niveau)
    
    # Validation
    if not titre or not description:
        return JsonResponse({
            'success': False,
            'error': 'Le titre et la description sont obligatoires'
        }, status=400)
    
    # Vérifier si le code existe déjà
    if code and Module.objects.filter(code=code).exists():
        return JsonResponse({
            'success': False,
            'error': 'Ce code de cours existe déjà'
        }, status=400)
    
    # Créer le module
    module = Module.objects.create(
        titre=titre,
        description=description,
        code=code,
        domaine=domaine,
        niveau=niveau,
        # fichier=fichier,
        auteur=request.user
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Module créé avec succès',
        'module': {
            'id': module.id,
            'titre': module.titre,
            'description': module.description,
            'code': module.code,
            'domaine': module.domaine,
            'niveau': module.niveau,
            'date_creation': module.date_creation.isoformat(),
            # 'fichier_url': module.fichier.url if module.fichier else None,
            #'fichier_nom': os.path.basename(module.fichier.name) if module.fichier else None
        }
    })
        
    # except Exception as e:
    #     return JsonResponse({
    #         'success': False,
    #         'error': str(e)
    #     }, status=500)

@login_required
@require_http_methods(["DELETE"])
def delete_module(request, module_id):
    """Supprimer un module"""
    try:
        module = Module.objects.get(id=module_id, auteur=request.user)
        
        # Supprimer le fichier s'il existe
        if module.fichier:
            if default_storage.exists(module.fichier.name):
                default_storage.delete(module.fichier.name)
        
        # Supprimer le module
        module.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Module supprimé avec succès'
        })
        
    except Module.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Module non trouvé'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["PUT"])
def update_module(request, module_id):
    """Mettre à jour un module"""
    try:
        module = Module.objects.get(id=module_id, auteur=request.user)
        data = json.loads(request.body)
        
        # Mettre à jour les champs
        if 'titre' in data:
            module.titre = data['titre']
        if 'description' in data:
            module.description = data['description']
        if 'code' in data:
            module.code = data['code']
        if 'domaine' in data:
            module.domaine = data['domaine']
        if 'niveau' in data:
            module.niveau = data['niveau']
        
        module.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Module mis à jour avec succès'
        })
        
    except Module.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Module non trouvé'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    

    
def boat(request):

    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('message', '')
        print('La question: ', question)
        
        #llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


        

        #folder_path = os.path.join(settings.MEDIA_ROOT, "chat_boat_azure")
        #vectordb =FAISS.load_local(folder_path, embeddings , allow_dangerous_deserialization=True )
        memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        return_messages=True
        )
        
        qa = ConversationalRetrievalChain.from_llm(
            llm_azure,
            retriever=vectordb.as_retriever(),
            return_source_documents=True,
            #chain_type_kwargs={"prompt": prompt},
            return_generated_question=True,
            memory=memory,
        
        )
    
        #question = "Qu'est ce que la cuisine?"
        result = qa.invoke({"question": question})
        

        return JsonResponse({'response': result["answer"],})


def profile(request):
    # membre=""
    # try: 
    #     membre = get_object_or_404(Etudiant, username=request.user)
    # except:
    #     membre = get_object_or_404(Professeur, username=request.user)
    # finally:
    #      pass
    
    # if request.method == 'POST':
    #     # Récupérer les données du formulaire
    #     user = get_object_or_404(User, username=request.user)
    #     print(request.POST.get('firstname'), user)
    #     user.first_name = request.POST.get('firstname',  membre.username.first_name)
    #     user.last_name = request.POST.get('lastname', membre.username.last_name)
    #     user.save()
    #     membre.phone = request.POST.get('phone', membre.phone)
    #     membre.numero_de_carte = request.POST.get('numero_de_carte', membre.numero_de_carte)
        
    #     # Sauvegarder les modifications
    #     membre.save()
    #     messages.info(request, f"Modifications enregistrés !")
    #     return redirect('index')  # Redirige vers la page du profil (ou une autre page)
    
    context = {}
    # if request.user.is_staff:
    #     context = {'is_staff': request.user.is_staff, 'membre': membre}
       
    # else:
    #     progress_percentage=0
       
    #     etudiant = Etudiant.objects.get(username = request.user)
    #     max_score = QuestionAnswers.objects.aggregate(total=Sum('score'))['total']
    #     print("Max_score: ", max_score)
    #     try:
    #         total_score = sum(score['score'] for score in etudiant.scores)
    #         progress_percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    #     except:
    #         pass
    #     context = {'progress_percentage': round(progress_percentage, 2),
    #                'is_staff': request.user.is_staff,'membre': membre
    #                }
    

    return render(request, 'profile.html', context)
def dashboard(request):
     modules = Module.objects.filter(auteur=request.user)
     courses = Cours.objects.filter(author=request.user)
     print("Modules: ", courses)
     return render(request, template_name="prof_dash.html", context = {"modules": modules, "courses": courses})


from django.http import JsonResponse
from .models import Module

from django.conf import settings

def module_details(request, code):
    try:
        module = Module.objects.get(code=code)
        data = {
            "titre": module.titre,
            "cours": list(module.cours.values("titre", "contenu", "file")),  # Ajout du fichier
           "exercices": [{"titre": e.titre,"question": json.loads(e.question),  "reponse_attendue": e.reponse_attendue}for e in module.exercices.all()],
            "quizz": list(module.quizz.values("question", "choix", "bonne_reponse")),
            "evaluations": list(module.evaluations.values("titre", "consignes", "contenu")),
        }

        # 🔹 Générer l'URL du fichier correctement
        for cours in data["cours"]:
            if cours.get("file"):
                file_instance = module.cours.get(titre=cours["titre"]).file  # Récupération du FileField
                host = request.get_host()
                cours["file_url"] = f"{host}" + settings.MEDIA_URL + str(file_instance)  # Génération de l'URL complète
                cours["file"] = f"{host}" + settings.MEDIA_URL + str(file_instance)  # Génération de l'URL complète
        print("Data: ", data)        

        return JsonResponse(data)

    except Module.DoesNotExist:
        return JsonResponse({"error": "Module introuvable"}, status=404)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Module, Cours, Exercice, Quiz, Evaluation

@csrf_exempt
def create_content(request):
    if request.method == "POST":
        data = request.POST
        content_type = data.get("contentType")
        module_code = data.get("module_code")
        print("Content Type: ", content_type, "Module Code: ", module_code)
        print("Data: ", data)
        try:
            module = Module.objects.get(code=module_code)

            if content_type == "cours":
                file = request.FILES.get("file")
                if not file:
                    return JsonResponse({"error": "Fichier PDF requis pour les cours"}, status=400)

                # 🔹 Création du cours et sauvegarde du fichier
                cours = Cours.objects.create(
                    module=module,
                    titre=data.get("title"),
                    contenu=data.get("description"),
                    file=file,
                    author=request.user
                )
                count = Cours.objects.filter(module=module).count()
                filepath = cours.file.path
                persist_path = os.path.join("media", "chroma", module_code+f"_{count}")

                # 🔥 Indexation du document pour RAG
                documents = load_pdf_documents(filepath)
                create_vectorstore(documents, persist_path)

                return JsonResponse({
                    "success": True,
                    "type": "cours",
                    "content": {"titre": cours.titre, "code": module_code, "domain": module.domaine, "file_url": cours.file.url}
                })

            elif content_type == "exercice":
                persist_path = os.path.join("media", "chroma", module_code+"_1")  # 🔹 Récupération de l'index des cours liés
                # question_prompt = f"Génère une question d'exercice basée sur les connaissances du module {module_code}."
                question_prompt = f"""
                Génère un exercice à questions détaillées de type '{data.get("exerciseType")[0]}' pour le module '{module.titre}' en '{data.get("domain")[0]}'.

                L'exercice doit correspondre à un niveau '{data.get("aiDifficulty")[0]}' et contenir {data.get("questionCount")[0]} questions sous forme de '{data.get("questionType")[0]}'.

                Le type d'évaluation attendu est '{data.get("evaluationType")[0]}' avec un score maximal de {data.get("maxScore")[0]} points.

                Description de l'exercice : {data.get("description")[0]}.

                Renvoi l'exercice sous le format ci dessus et assure-toi que les questions respectent le niveau attendu.
                Format de l'exerice attendu:
               
                [
                "Contexte ou introduction ou consigne de l'exercice",
                "1. Texte de la question 1",
                "2. Texte de la question 2",
                "3. Texte de la question 3",
                ...
                ]
                
                """

                print("Question Prompt: ", question_prompt)

                # 🔥 Récupération du contexte via RAG
                rag_response = rag_answer(question_prompt, persist_path, llm)

                print(rag_response)
               
                 
                # 🔹 Création de l'exercice avec la réponse générée
                exercice = Exercice.objects.create(
                    titre = data.get("title"),
                    module=module,
                   question=json.dumps(rag_response),
                    reponse_attendue="Réponse attendue à compléter."
                )

                return JsonResponse({
                    "success": True,
                    "type": "exercice",
                    "content": {"titre": exercice.titre, "code": module_code, "question": exercice.question, "reponse_attendue": exercice.reponse_attendue}
                })

            elif content_type == "quiz":
                quiz = Quiz.objects.create(
                    module=module,
                    question=data.get("title"),
                    choix={"A": "Choix A", "B": "Choix B", "C": "Choix C", "D": "Choix D"},
                    bonne_reponse="A"
                )
                return JsonResponse({
                    "success": True,
                    "type": "quiz",
                    "content": {"titre": quiz.question, "code": module_code}
                })

            elif content_type == "evaluation":
                evaluation = Evaluation.objects.create(
                    module=module,
                    titre=data.get("title"),
                    consignes=data.get("description"),
                    contenu={"questions": []}
                )
                return JsonResponse({
                    "success": True,
                    "type": "evaluation",
                    "content": {"titre": evaluation.titre, "code": module_code}
                })

        except Module.DoesNotExist:
            return JsonResponse({"error": "Module introuvable"}, status=404)

    return JsonResponse({"error": "Requête invalide"}, status=400)



def connection(request):
    mess = ""

    '''if request.user.is_authenticated:
         return redirect("dashboard")'''
    if request.method == "POST":
        
        print("="*5, "NEW CONECTION", "="*5)
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        try:
            validate_email(email)
        except:
            mess = "Invalid Email !!!"
        #authen = User.lo
        if mess=="":
            from django.contrib.auth import get_user_model
            User = get_user_model()

            user = User.objects.filter(email= email).first()
            if user:
                auth_user= authenticate(username= user.username, password= password)
                if auth_user:
                    print("Utilisateur infos: ", auth_user.username, auth_user.email)
                    login(request, auth_user)
                    
                    return redirect("home")
                else :
                    mess = "Incorrect password"
            else:
                mess = "user does not exist"
            
        messages.info(request, mess)

    return render(request, template_name="login.html")

def register(request):
    mess = ""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if request.method == "POST":
        
        print("="*5, "NEW REGISTRATION", "="*5)
        
        prenom= request.POST.get("firstname", None)
        nom= request.POST.get("lastname", None)
        username = ''.join(f"{nom}{prenom}".split())
        email = request.POST.get("email", None)
        pass1 = request.POST.get("password1", None)
        pass2 = request.POST.get("password2", None)
        phone = request.POST.get("phone", None)  # Récupérez le champ "Numéro de téléphone"
        job = request.POST.get("job", None)  # Récupérez le champ "Numéro de téléphone"
        prof_code = request.POST.get("prof_code", None)  # Récupérez le champ "Code Professeur"
        print(username, email, pass1, pass2, prof_code)
        try:
            validate_email(email)
        except:
            mess = "Invalid Email"
        if pass1 != pass2 :
            mess += " Password not match"
        if User.objects.filter(Q(email= email)| Q(username=username)).first():
            mess += f" Exist user with email {email} or username {username}"
        print("Message: ", mess)
        if mess=="":
            try:
                    validate_password(pass1)
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=pass1,
                        first_name=prenom,
                        last_name=nom
                    )

                    if prof_code:
                         user.groups.add(prof_group)
                    else:
                         user.groups.add(student_group)
                    user.save()
                    profile = Profile.objects.create(user = user, job= job, phone=phone)
                    profile.save()
                    subject = "Bienvenue sur kalanso !"

                    email_message = f"""
                    <!DOCTYPE html>
                    <html lang="fr">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Bienvenue sur kalanso !</title>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                background-color: #f4f7fa;
                                color: #333;
                                margin: 0;
                                padding: 0;
                            }}
                            .container {{
                                max-width: 600px;
                                margin: 20px auto;
                                padding: 20px;
                                background-color: #ffffff;
                                border-radius: 8px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            }}
                            h1 {{
                                color: #d9534f;
                                text-align: center;
                            }}
                            p {{
                                font-size: 16px;
                                line-height: 1.6;
                                margin: 10px 0;
                            }}
                            ul {{
                                font-size: 16px;
                                margin: 10px 0;
                            }}
                            li {{
                                margin-bottom: 8px;
                            }}
                            .highlight {{
                                font-weight: bold;
                                color: #d9534f;
                            }}
                            .footer {{
                                text-align: center;
                                font-size: 14px;
                                margin-top: 20px;
                                color: #888;
                            }}
                            .button {{
                                display: inline-block;
                                padding: 12px 20px;
                                margin-top: 20px;
                                background-color: #d9534f;
                                color: #fff;
                                text-decoration: none;
                                border-radius: 4px;
                                text-align: center;
                            }}
                            .button:hover {{
                                background-color: #c9302c;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>Bienvenue sur kalanso, {prenom} ! 👩‍🍳👨‍🍳</h1>
                            <p>Bonjour {prenom},</p>
                            <p>Bienvenue sur <span class="highlight">kalanso</span>, la plateforme innovante qui vous accompagne dans votre apprentissage culinaire ! Nous sommes ravis de vous avoir parmi nous et convaincus que cette aventure sera aussi savoureuse qu’enrichissante.</p>
                            <p><span class="highlight">kalanso</span> utilise une technologie avancée, le modèle RAG (Retrieval-Augmented Generation), pour vous proposer des quiz personnalisés à partir des cours publiés par vos professeurs. Cela vous permet de tester vos connaissances de manière interactive et dynamique, tout en renforçant les compétences acquises dans chaque leçon.</p>
                            <p><strong>Voici ce que vous pouvez attendre de kalanso :</strong></p>
                            <ul>
                                <li><span class="highlight">Des quiz adaptés à vos cours :</span> Chaque question générée est directement liée au contenu de vos leçons, garantissant une révision ciblée et efficace.</li>
                                <li><span class="highlight">Une progression suivie en temps réel :</span> Vous pourrez suivre votre performance et identifier les sujets à approfondir pour progresser.</li>
                                <li><span class="highlight">Une expérience d’apprentissage flexible :</span> Les quiz sont accessibles à tout moment, pour vous permettre d’apprendre à votre rythme et selon vos disponibilités.</li>
                            </ul>
                            <p>Pour commencer, explorez vos cours disponibles sur votre tableau de bord, et laissez-vous guider par les quiz adaptés à chaque leçon. Plus vous interagissez avec le contenu, plus vous renforcez vos compétences culinaires !</p>
                            <p>Si vous avez des questions ou besoin d’aide, n’hésitez pas à nous contacter. Notre équipe est là pour vous accompagner à chaque étape de votre apprentissage.</p>
                            <p>Bon apprentissage et à très bientôt sur <span class="highlight">kalanso</span> !</p>
                            <div class="footer">
                                <p>Cordialement,</p>
                                <p>L’équipe kalanso</p>
                                <p>03 27 51 77 47</p>
                                <p><a href="https://kalanso.de" target="_blank">https://kalanso.de</a></p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """

                    #emailsender(subject, email_message, email_address,  user.email)

                    mess = f"Welcome, {prenom}! Your account has been successfully created" #. To activate your account, please retrieve your verification code from the email sent to {user.email}"
                        
                    messages.info(request, mess)

                    verification_code, created = VerificationCode.objects.get_or_create(user=user)
                    verification_code.generate_code()
                    print(verification_code.code)
                    
                    subject = "Votre code de vérification kalanso"

                    email_message = f"""
                    <!DOCTYPE html>
                    <html lang="fr">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Code de vérification</title>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                background-color: #f4f7fa;
                                color: #333;
                                margin: 0;
                                padding: 0;
                            }}
                            .container {{
                                max-width: 600px;
                                margin: 20px auto;
                                padding: 20px;
                                background-color: #ffffff;
                                border-radius: 8px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            }}
                            h1 {{
                                color: #d9534f;
                                text-align: center;
                            }}
                            p {{
                                font-size: 16px;
                                line-height: 1.6;
                                margin: 10px 0;
                            }}
                            .code-box {{
                                text-align: center;
                                margin: 20px 0;
                            }}
                            .code {{
                                display: inline-block;
                                font-size: 24px;
                                font-weight: bold;
                                background-color: #f8f9fa;
                                padding: 10px 20px;
                                border: 1px solid #ddd;
                                border-radius: 5px;
                                color: #d9534f;
                                letter-spacing: 2px;
                            }}
                            .footer {{
                                text-align: center;
                                font-size: 14px;
                                margin-top: 20px;
                                color: #888;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>Votre code de vérification</h1>
                            <p>Bonjour {prenom},</p>
                            <p>Voici votre code de vérification pour accéder à votre compte kalanso. Entrez ce code sur notre site pour compléter votre connexion ou validation :</p>
                            <div class="code-box">
                                <span class="code">{verification_code.code}</span>
                            </div>
                            <p>Ce code est valide pendant les <strong>30 prochaines minutes</strong>. Si vous n’avez pas demandé ce code, veuillez ignorer cet e-mail ou nous contacter immédiatement.</p>
                            <div class="footer">
                                <p>Merci de faire confiance à <strong>kalanso</strong> !</p>
                                <p>03 27 51 77 47 | <a href="https://kalanso.de" target="_blank">https://kalanso.de</a></p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """

                    #emailsender(subject, email_message, email_address, user.email)
                                    
                    return redirect("login")
            except Exception as e:
                    print("error: ", type(e), e)
                    #err = " ".join(e)
                    
                    messages.error(request, f"Erreur survenue lors de la creation de compte, veuillez reessayer.")
                    return render(request, template_name="/register.html")
            
        else:
            messages.info(request, mess)

    return render(request, template_name="register.html")


def logout_view(request):
    logout(request)  # Déconnexion de l'utilisateur
    return redirect('home')


from django.core.mail import send_mail  # Use Django's email sending
from django.utils.html import strip_tags # For plain text version
from django.template.loader import render_to_string # For cleaner HTML

def forgotpassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            current_site = request.META["HTTP_HOST"] # Replace with your actual domain
            subject = "Password Reset Wufa"

            # Use a template for cleaner HTML
            html_message = render_to_string('account/password_reset_email.html', {
                'user': user,
                'reset_link': f"{current_site}/updatepassword/{token}/{uid}/",
            })

            plain_message = strip_tags(html_message) # Create plain text version

            send_mail(
                subject,
                plain_message,  # Send plain text version
                email_address,  # From email
                [user.email],  # To email(s)
                html_message=html_message,  # Send HTML version
            )

            messages.success(request, f"A reset password email has been sent to {user.email}.")
        else:
            messages.success(request, "The email address does not match any account.")

    return render(request, "account/forgot_password.html")

def updatepassword(request, token, uid):
    print(request.user.username, token, uid)
    try:
            user_id = urlsafe_base64_decode(uid)
            decode_uid = codecs.decode(user_id, "utf-8")
            user = User.objects.get(id= decode_uid)
                         
    except:
            return HttpResponseForbidden("You are not authorize to edit this page")
    print("Utilisateur: ", user)
    checktoken = default_token_generator.check_token( user, token)
    if not checktoken:
        return HttpResponseForbidden("You are not authorize to edit this page, your token is not valid or have expired")
    if request.method =="POST":
            user = User.objects.get(id= decode_uid)
            pass1= request.POST.get('pass1')
            pass2= request.POST.get('pass2')
            if pass1 == pass2:
                 try:
                        validate_password(pass1)
                        user.password = pass1
                        user.set_password(user.password)
                        user.save()
                        messages.success(request, "Your password is update sucessfully")
                 except ValidationError as e:
                      messages.error(request, str(e))
                      
                       
                 return redirect('login')
            else:
                 messages.eror(request, "Passwords not match")
        
    return render(request, "account/update_password.html")
