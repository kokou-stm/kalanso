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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils.pdf_utils import load_pdf_documents
from .utils.rag import create_vectorstore, rag_answer
import os


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

prof_group, created = Group.objects.get_or_create(name='Professeur')
student_group, created = Group.objects.get_or_create(name='Etudiant')


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

from django.utils.translation import gettext as _

@login_required
def index(request):
    indentifiant = str(request.user.username)[:2]
    user = request.user
    context = {
        'user': user,
        'is_staff': user.is_staff,
    }
    
    context["identifiant"]= indentifiant
    if request.user.groups.filter(name='Professeur').exists():
        prof = _("Professeur")
        context['status'] = prof
        modules = Module.objects.filter(auteur=request.user)
        courses = Cours.objects.filter(author=request.user)
        print("Modules: ", courses)
        context.update({"modules": modules, "courses": courses})
        return render(request, template_name="prof_dash.html", context = context )
        
        
    elif request.user.groups.filter(name='Etudiant').exists():
        context['status'] = "Etudiant"
        return render(request, "student_dashboard.html")
    return render(request, "student_dashboard.html")
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
@require_http_methods(["POST"])
def create_module(request):
    """Créer un nouveau module"""
    try:
        # Récupération des données
        titre = request.POST.get('titre', '').strip()
        description = request.POST.get('description', '').strip()
        code = request.POST.get('code', '').strip()
        domaine = request.POST.get('domaine', '').strip()
        niveau = request.POST.get('niveau', '').strip()
        
        # Log pour debugging
        print(f"Données reçues: {request.POST}")
        print(f"Titre: {titre}, Description: {description}, Code: {code}")
        
        # Validation des champs obligatoires
        if not titre:
            return JsonResponse({
                'success': False,
                'error': 'Le titre est obligatoire'
            }, status=400)
            
        if not description:
            return JsonResponse({
                'success': False,
                'error': 'La description est obligatoire'
            }, status=400)
        
        # Vérifier si le code existe déjà (si fourni)
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
            auteur=request.user
        )
        
        # Log de succès
        print(f"Module créé avec succès: ID={module.id}, Titre={module.titre}")
        
        # Préparer la réponse avec toutes les données nécessaires
        module_data = {
            'id': module.id,
            'titre': module.titre,
            'description': module.description,
            'code': module.code,
            'domaine': module.domaine,
            'niveau': module.niveau,
            'date_creation': module.date_creation.isoformat(),
            'auteur': module.auteur.username if module.auteur else None,
            # Ajouter d'autres champs si nécessaire
        }
        
        return JsonResponse({
            'success': True,
            'message': 'Module créé avec succès',
            'module': module_data
        }, status=201)
        
    except Exception as e:
        # Log de l'erreur
        print(f"Erreur lors de la création du module: {str(e)}")
        
        return JsonResponse({
            'success': False,
            'error': f'Erreur serveur: {str(e)}'
        }, status=500)


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Module

@login_required
def api_modules(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        modules = Module.objects.filter(auteur=request.user)
        data = [
            {
                "titre": m.titre,
                "code": m.code,
                "nb_etudiants": getattr(m, 'nb_etudiants', 0),
                "nb_quiz": getattr(m, 'nb_quiz', 0),
                "progress": getattr(m, 'progress', 0)
            }
            for m in modules
        ]
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'Requête invalide'}, status=400)


# Fonction utilitaire pour lister les modules (si nécessaire)
@login_required
@require_http_methods(["GET"])
def list_modules(request):
    """Lister tous les modules de l'utilisateur"""
    try:
        # Récupérer les modules de l'utilisateur connecté
        modules = Module.objects.filter(auteur=request.user).order_by('-date_creation')
        
        # Sérialiser les données
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
                'auteur': module.auteur.username,
            })
        
        return JsonResponse({
            'success': True,
            'modules': modules_data,
            'count': len(modules_data)
        })
        
    except Exception as e:
        print(f"Erreur lors de la récupération des modules: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Erreur lors du chargement des modules'
        }, status=500)
    

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
            "cours": list(module.cours.values("titre", "contenu", "file", "code")),  # Ajout du fichier
            "exercices": [{"titre": e.titre,"question": json.loads(e.question),  "reponse_attendue": e.reponse_attendue}for e in module.exercices.all()],
            "quizz": list(module.quizz.values("questions", "max_score", "quiz_title")),
           # "evaluations": list(module.evaluations.values("titre", "consignes", "contenu")),
        }
        print(data['quizz'])
        # 🔹 Générer l'URL du fichier correctement
        for cours in data["cours"]:
            if cours.get("file"):
                file_instance = module.cours.get(titre=cours["titre"]).file  # Récupération du FileField
                host = request.get_host()
                cours["file_url"] = f"{host}" + settings.MEDIA_URL + str(file_instance)  # Génération de l'URL complète
                cours["file"] = f"{host}" + settings.MEDIA_URL + str(file_instance)  # Génération de l'URL complète
        #print("Data: ", data)        

        return JsonResponse(data)

    except Module.DoesNotExist:
        return JsonResponse({"error": "Module introuvable"}, status=404)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .utils.prompt import feedback_prompt
from .utils.rag import *
from .utils.ai_prompt import *

import json
import re
from openai import AzureOpenAI
2

def extract_json(text):
    """
    Extrait un objet JSON valide depuis un texte potentiellement bruité.
    """
    try:
        # Essai direct
        print("$$", "debut transformation")
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Recherche d'un bloc JSON avec des accolades
    match = re.search(r"\{[\s\S]+\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Si rien ne marche
    print("Impossible d'extraire du JSON valide depuis le texte renvoyé.")
    raise ValueError("Impossible d'extraire du JSON valide depuis le texte renvoyé.")


def relevant_docs(path):
    print("__"*10)
    llm_azure = AzureChatOpenAI(
        openai_api_version="2024-07-01-preview",
        deployment_name="gpt-35-turbo-chefquiz",
        openai_api_key=settings.AZURE_EMBEDDING_API_KEY,
        openai_api_type='azure',
        azure_endpoint="https://realtimekokou.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2024-08-01-preview",
    )

    # URL du fichier FAISS dans Azure Blob Storage
    faiss_url = f"https://chefquizstockage.blob.core.windows.net/media/{path}/index.faiss"
    pickle_url = f"https://chefquizstockage.blob.core.windows.net/media/{path}/index.pkl"

    # Créer un chemin temporaire local pour les fichiers téléchargés
    folder_path = os.path.join(settings.MEDIA_ROOT, path)
    temp_file_path_faiss = os.path.join(folder_path, "index.faiss")
    temp_file_path_pickle = os.path.join(folder_path, "index.pkl")

    print(folder_path, )
    # Télécharger les fichiers depuis Azure Blob Storage
    download_file_from_url(faiss_url, temp_file_path_faiss)
    download_file_from_url(pickle_url, temp_file_path_pickle)
    print("=="*10, "downlad")
    # Charger l'index FAISS localement depuis le fichier téléchargé
    vectordb = FAISS.load_local(folder_path, embeddings, allow_dangerous_deserialization=True)
    
    # Supprimer les fichiers locaux temporaires après utilisation
    if os.path.exists(temp_file_path_faiss):
        os.remove(temp_file_path_faiss)
        print(f"Fichier local temporaire {temp_file_path_faiss} supprimé.")

    if os.path.exists(temp_file_path_pickle):
        os.remove(temp_file_path_pickle)
        print(f"Fichier local temporaire {temp_file_path_pickle} supprimé.")

    # Exécuter la chaîne de questions-réponses
    qa_chain = RetrievalQA.from_chain_type(
        llm_azure,
        retriever=vectordb.as_retriever(),
        return_source_documents=True,
    )
    print("="*4, qa_chain, "="*4)
    result = qa_chain.invoke({
        "query": "Donne moi les parties les plus pertinentes de ce document un peu difficiles à comprendre",
        "search_kwargs": {"k": 8}
    })

    documents = " ".join([docs.page_content for docs in result['source_documents']])
    print(result)
    return documents


def chat_with_openai(number, difficulty, path):
    AZURE_CHAT_ENDPOINT = "https://realtimekokou.openai.azure.com/openai/deployments/gpt-4-0613/chat/completions?api-version=2024-10-21"
    AZURE_CHAT_API_KEY = "h5R1YOBt2Q5WU56488stKWc7GiO9nEG3Z344ITLK3mTb6uGkdlKLJQQJ99BAACYeBjFXJ3w3AAABACOGLM5j"

    client = AzureOpenAI(
        api_key=AZURE_CHAT_API_KEY,
        api_version="2024-10-21",
        azure_endpoint=AZURE_CHAT_ENDPOINT
    )

    print('path: ', path, "==" * 4)
    context = relevant_docs(path)
    print("Context: ", context)

    prompt = f"""
    Génère un quiz de {number} questions basé sur ce texte :

    {context}

    Niveau de difficulté : {difficulty}.
    Le quiz doit être en français.
    Le format de sortie doit être exactement :
    {json.dumps(RESPONSE_JSON, ensure_ascii=False, indent=2)}

    Ne mets **rien d’autre** autour du JSON.
    Les options doivent être des phrases complètes, pas juste des mots.
    """

    print("Seconde step: ", "==" * 5)

    chat_completion = client.chat.completions.create(
        model="gpt-4-0613",
        messages=[
            {"role": "system", "content": "Tu es un expert en création de QCM."},
            {"role": "user", "content": prompt},
        ]
    )

    print("Initialisation terminée.")
    response_text = chat_completion.choices[0].message.content
    print("Réponse OpenAI :\n", response_text)

    json_data = extract_json(response_text)
    # except ValueError as e:
    #     print("Erreur d'extraction JSON :", e)
    #     json_data = None
    print("=="*10)
    return json_data



@csrf_exempt
def create_content(request):
   
    if request.method == "POST":
        data = request.POST
        content_type = data.get("contentType")
        module_code = data.get("module_code")
        
        #print("Content Type: ", content_type, "Module Code: ", module_code)
        print("=="*10)
        print("Données: ", data)
        print("=="*10)
        TAXONOMY_CHOICES = {
                   'connaissance':'remember',
                    'comprehension': 'understand', 
                     'application': 'apply',
                     'analyse': 'analyse',
                     'Évaluation': 'evaluate',
                     'Créer': 'create',
                }
        try:
            module = Module.objects.get(code=module_code)

            if content_type == "cours":
                file = request.FILES.get("file")
                if not file:
                    return JsonResponse({"error": "Fichier PDF requis pour les cours"}, status=400)
                cours_code = data.get("code")
                # 🔹 Création du cours et sauvegarde du fichier
                cours = Cours.objects.create(
                    code =cours_code,
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
                
                result = rag_with_qa(persist_path, llm, feedback_prompt)
                print(result)
                cours.feedback = result
                cours.save()

                taxonomies_levels = ["remember", "understand", "apply", "analyse", "evaluate", "create"]
                for index, tax in enumerate(taxonomies_levels):
                    PromptMemoire.objects.get_or_create(cours= cours,niveau_taxonomie=tax, prompt = prompts[index] )

                return JsonResponse({
                    "success": True,
                    "type": "cours",
                    "content": {"titre": cours.titre, "code": module_code, "domain": module.domaine, "file_url": cours.file.url},
                    "feedback": result
                })

            elif content_type == "exercice":
                cours_id = data.get("course_id")
                
                cours = Cours.objects.get(id = int(cours_id))
                
                
                
                bloomLevel = TAXONOMY_CHOICES[data.get("bloomLevel").lower()]
                
                prompt_update = PromptMemoire.objects.filter(cours = cours, niveau_taxonomie = bloomLevel)[0]
                print("Les prompts: ", prompts)
                persist_path = os.path.join("media", "chroma", module_code+"_1")  # 🔹 Récupération de l'index des cours liés
                # question_prompt = f"Génère une question d'exercice basée sur les connaissances du module {module_code}."
                question_prompt = f"""
                Génère un exercice à questions détaillées dans la langue {data.get("lang")[:]} de type '{data.get("exerciseType")[0]}' pour le module '{module.titre}' en '{data.get("domain")[0]}'.

                L'exercice doit correspondre à un niveau '{data.get("aiDifficulty")[0]}' et contenir {data.get("questionCount")[:]} questions sous forme de '{data.get("questionType")[0]}'.

                Le type d'évaluation attendu est '{data.get("evaluationType")[0]}' avec un score maximal de {data.get("maxScore")[0]} points.

                Description de l'exercice : {data.get("description")[0]}.
                
                les questions doivent etre un peu dans le sens:
                {prompt_update.prompt} .
                Voici quelques exemples de types de questions proposés par l'enseignant: 
                
                {prompt_update.retour_enseignant}
                

                Renvoi l'exercice sous le format ci dessus et assure-toi que les questions respectent le niveau attendu.
                Le test  de chaque question doit etre complete donc longue si possible.
                Format de l'exercice attendu:
                [
                "consigne de l'exercice",
                "1. Texte de la question 1",
                "2. Texte de la question 2",
                "3. Texte de la question 3",
                ...
                ]
            
                Rapelle toi que tu dois générer {data.get("questionCount")[:]} questions

                L'exercice doit etre uniquement dans la langue : {data.get("lang")[:]}

                """

                print("Langue : ", data.get("lang")[:])
                print("--"*10)

                # 🔥 Récupération du contexte via RAG
                rag_response = rag_answer(question_prompt, persist_path, llm)

                print(rag_response)
                
               
                # 🔹 Création de l'exercice avec la réponse générée
                exercice = Exercice.objects.create(
                    titre = data.get("title"),
                    module=module,
                   question=json.dumps(rag_response[1:]),
                    reponse_attendue="Réponse attendue à compléter."
                )
                print("=="*10)
                print(exercice.question)
                print("=="*10)

                return JsonResponse({
                    "success": True,
                    "type": "exercice",
                    "content": {"titre": exercice.titre, "code": module_code, "question": exercice.question, "reponse_attendue": exercice.reponse_attendue}
                })

            elif content_type == "quiz":
                print("--"*8, "quiz", "-"*8)
                cours_id = data.get("course_id")
                cours = Cours.objects.filter(id = cours_id)[0]
                bloomLevel = TAXONOMY_CHOICES[data.get("bloomLevel").lower()]
                prompt_update = PromptMemoire.objects.filter(cours = cours, niveau_taxonomie = bloomLevel)[0]
                persist_path = os.path.join("media", "chroma", module_code+"_1") 
                question_prompt = f"""
                

                
                ---

               Tu es un assistant pédagogique intelligent qui génère les quiz..

                ---

                🎯 **CONSIGNES DE CONCEPTION** :

                Analyse les éléments suivants pour personnaliser le quiz :
                - Niveau de maîtrise actuel de l'élève
                - Progression d'apprentissage
                - Objectifs pédagogiques associés
                - Exemples de questions types fournis par l'enseignant

                Utilise ce prompt de référence pédagogique :
                {prompt_update.prompt}

                Et les exemples fournis par l'enseignant :
                {prompt_update.retour_enseignant}

                ---

                🎲 **SÉLECTION DES FORMATS DE QUESTIONS** :

                - Pour les niveaux *Se souvenir / Comprendre* :
                    - QCM à réponse unique
                    - Vrai/faux avec justification
                    - Remplissage des blancs
                    - Questions courtes

                - Pour les niveaux *Appliquer / Analyser* :
                    - QCM scénarisés
                    - Études de cas
                    - Résolution de problèmes

                - Pour les niveaux *Évaluer / Créer* :
                    - Mini-dissertations
                    - Défis créatifs
                    - Tâches ouvertes

                Tu dois mélanger les types suivants :
                - `mcq` : QCM à une seule bonne réponse
                - `multi_mcq` : QCM à plusieurs bonnes réponses
                - `fill_blank` : Complétion de phrase
                - `short_answer` : Réponse courte

                ---

                ✅ **CRITÈRES DE QUALITÉ** :

                Chaque question doit respecter :
                - L’alignement avec le niveau de Bloom demandé
                - Un langage clair, sans ambiguïté
                - Une pertinence pédagogique forte
                - Une difficulté adaptée à la progression de l’élève
                - Une capacité à différencier les niveaux de compréhension
                - Une authenticité liée à des situations réelles si possible

                ---
                
                Ta tâche est de générer un **quiz personnalisé** pour le module **'{module.titre}'** contenant {data.get("questionCount")[:]} questions QCM, dans le domaine **'{data.get("domain")[0]}'**.

                Ce quiz vise un niveau **{bloomLevel}** selon la **Taxonomie de Bloom**, avec un **niveau de difficulté '{data.get("aiDifficulty")[0]}'**, adapté au niveau actuel de l’élève.
                
                 **MÉTADONNÉES DU QUIZ** :
                - Sujet : {data.get("domain")[0]}
                - Niveau Cognitif : {bloomLevel}
                - Dimension de Connaissance : {data.get("evaluationType")[0]}
                - Objectif pédagogique visé : {bloomLevel}
                - Difficulté estimée : {data.get("aiDifficulty")[0]}
                - Type d’évaluation : {data.get("evaluationType")[0]}
                - Score maximal : {data.get("maxScore")[0]} points
                - Nombre de questions : {data.get("questionCount")[:]} questions

                *** Tout le texte du quiz doit etre en **Markdown** (pour les blakn filling, les checkbox, les inputs...) ***
                \n -----------------\n 
                - Utilise toujours les  (") et non les single quote ('), comme c'est un json
                \n -----------------\n 
                **FORMAT DE SORTIE JSON DU QUIZ ATTENDU** :

                [
                    {{
                        "no": 1,
                        "type": "mcq" | "multi_mcq" | "fill_blank" | "short_answer",
                        "question": "*Texte de la question*",
                        "options": [  
                             Berlin  ,
                           Madrid  ,
                            Paris  ,
                            Rome 
                            ],  # uniquement si type = mcq ou multi_mcq
                        "correct": "Réponse attendue ou liste des réponses si multi_mcq",
                        "score": 10
                    }},
                    ...
                ]
                  
                 Assure-toi que le format est strictement respecté. Varie les types de questions et que le texte soit en **markdown**.
                 Assures-toi d'avoir generer {data.get("questionCount")[:]} nombres de questions.
                 Tout le texte du quiz doit etre en **Markdown** (pour les blakn filling, les checkbox, les inputs...)
                """

                print("Question Prompt:\n", question_prompt)
                print("--" * 10)

                # 🔥 Génération via RAG
                rag_response = rag_answer(question_prompt, persist_path, llm)

                print(rag_response)
               
               
                # Création du quiz
                quiz = Quiz_AI.objects.create(
                    quiz_title=data.get("title"),
                    quiz_description=data.get("description"),
                    course=cours,
                    max_score=sum(q['score'] for q in rag_response),
                    module = module,
                   
                )

                # Enregistrement des questions
                for q in rag_response:
                    QuestionAnswers.objects.create(
                        quiz=quiz,
                        numero=q['no'],
                        question_text=q['question'],
                        options=q.get('options'),  # JSONField accepte None si absent
                        great_answer=q['correct'],
                        score=q['score'],
                        required_time=60  # valeur par défaut, à adapter si besoin
                    )
                quiz.questions = [q.question_text for q in QuestionAnswers.objects.filter(quiz=quiz)]
                quiz.save()

                print("✅ Quiz et questions enregistrés avec succès.")

                return JsonResponse({
                "success": True,
                "type": "quiz",
                "quiz_title": data.get("title"),
                "content": {
                    "titre": [
                        {
                            "numero": q.numero,
                            "question_text": q.question_text,
                            "score": q.score,
                            "options": q.options,
                            "great_answer": q.great_answer,
                        }
                        for q in QuestionAnswers.objects.filter(quiz=quiz)
                    ],
                    "code": module_code
                }
            })


                # data = raw_response
                # # try:
                # #     data = json.loads(raw_response)
                # # except json.JSONDecodeError:
                # #     return JsonResponse({'error': 'Réponse JSON invalide du modèle IA.', 'raw': raw_response}, status=500)
                
                # print("==", "save begin", "==")
                # # Création des questions
                # for key, value in data.items():
                #     QuestionAnswers.objects.create(
                #         quiz=quiz,
                #         question_text=value.get('mcq', ''),
                #         numero=int(value.get("no", 0)),
                #         options=value.get("options", []),
                #         great_answer=value.get('correct', ''),
                #         required_time=60,
                #         score=10,
                #     )
                # quiz = Quiz.objects.create(
                #     module=module,
                #     question=data.get("title"),
                #     choix={"A": "Choix A", "B": "Choix B", "C": "Choix C", "D": "Choix D"},
                #     bonne_reponse="A"
                # )
                # return JsonResponse({
                #     "success": True,
                #     "type": "quiz",
                #     "content": {"titre": quiz.question, "code": module_code}
                # })

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



@login_required
@csrf_exempt
def save_training_data(request):

    """
    Sauvegarde les données d'entraînement fournies par l'enseignant
    """
    try:
        data = json.loads(request.body)
        course_code = data.get('course_code')
        training_data = data.get('training_data', {})
        #print("Data: ", data, course_code, training_data)
        print(training_data)
        if not course_code:
            return JsonResponse({
                'error': 'Code du cours manquant'
            }, status=400)
        
        # Récupérer le cours
        cours = get_object_or_404(Cours, code=course_code, author=request.user)
        
        # Taxonomies supportées
        taxonomies_levels = ["remember", "understand", "apply", "analyse", "evaluate", "create"]
        
        # Sauvegarder les données pour chaque niveau de taxonomie
        for index, level in enumerate(taxonomies_levels):
            if level in training_data and training_data[level]:
                # Récupérer ou créer le PromptMemoire pour ce niveau
                prompt_memoire, created = PromptMemoire.objects.get_or_create(
                    cours=cours,
                    niveau_taxonomie=level,
                    defaults={
                        'prompt': f'{prompts[index]}'
                    }
                )
                
                # Traitement des exemples existants et nouveaux
                existing_examples = []
                if prompt_memoire.retour_enseignant:
                    try:
                        existing_data = json.loads(prompt_memoire.retour_enseignant)
                        if isinstance(existing_data, list):
                            existing_examples = existing_data
                        elif isinstance(existing_data, dict) and 'examples' in existing_data:
                            existing_examples = existing_data['examples']
                    except json.JSONDecodeError:
                        existing_examples = []
                
                # Fusionner les nouveaux exemples avec les existants
                new_examples = training_data[level]
                all_examples = existing_examples.copy()
                
                # Éviter les doublons en comparant les questions
                existing_questions = {ex.get('question', '') for ex in existing_examples}
                for new_example in new_examples:
                    if new_example.get('question', '') not in existing_questions:
                        all_examples.append(new_example)
                
                # Sauvegarder dans retour_enseignant
                updated_data = {
                    'examples': all_examples,
                    'total_examples': len(all_examples),
                    'last_updated': str(timezone.now()),
                    'level_description': get_taxonomy_description(level)
                }
                
                prompt_memoire.retour_enseignant = json.dumps(updated_data, ensure_ascii=False)
                prompt_memoire.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Données d\'entraînement sauvegardées avec succès',
            'saved_levels': list(training_data.keys())
        })
        
    except Cours.DoesNotExist:
        return JsonResponse({
            'error': 'Cours non trouvé'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Format JSON invalide'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Erreur lors de la sauvegarde: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_taxonomy_examples(request, course_code, taxonomy_level):
    """
    Récupère les exemples pour un niveau de taxonomie spécifique
    """
    try:
        cours = get_object_or_404(Cours, code=course_code, author=request.user)
        
        try:
            prompt_memoire = PromptMemoire.objects.get(
                cours=cours,
                niveau_taxonomie=taxonomy_level
            )
            
            examples = []
            if prompt_memoire.retour_enseignant:
                try:
                    data = json.loads(prompt_memoire.retour_enseignant)
                    if isinstance(data, dict) and 'examples' in data:
                        examples = data['examples']
                    elif isinstance(data, list):
                        examples = data
                except json.JSONDecodeError:
                    pass
            
            return JsonResponse({
                'success': True,
                'examples': examples,
                'level': taxonomy_level,
                'total': len(examples)
            })
            
        except PromptMemoire.DoesNotExist:
            return JsonResponse({
                'success': True,
                'examples': [],
                'level': taxonomy_level,
                'total': 0
            })
            
    except Cours.DoesNotExist:
        return JsonResponse({
            'error': 'Cours non trouvé'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': f'Erreur: {str(e)}'
        }, status=500)
    
    
def get_taxonomy_description(level):
    """
    Retourne la description d'un niveau de taxonomie
    """
    descriptions = {
        'remember': 'Rappeler des faits, termes, concepts de base',
        'understand': 'Expliquer des idées ou concepts',
        'apply': 'Utiliser l\'information dans de nouvelles situations',
        'analyse': 'Décomposer l\'information en parties',
        'evaluate': 'Justifier une position ou décision',
        'create': 'Produire un travail original'
    }
    return descriptions.get(level, 'Description non disponible')


def get_feedback(request, code):
    try:
        cours = Cours.objects.get(code=code)
        return JsonResponse({'success': True, 'feedback': cours.feedback})
    except Cours.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cours non trouvé'}, status=404)


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
                    
                    return redirect("index")
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
                    return render(request, template_name="register.html")
            
        else:
            messages.info(request, mess)

    return render(request, template_name="register.html")


def logout_view(request):
    logout(request)  # Déconnexion de l'utilisateur
    return redirect('home')


from django.core.mail import send_mail  # Use Django's email sending
from django.utils.html import strip_tags # For plain text version
from django.template.loader import render_to_string # For cleaner HTML
from django.contrib.auth import get_user_model
User = get_user_model()

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
            html_message = render_to_string('password_reset_email.html', {
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

    return render(request, "forgot_password.html")

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
        
    return render(request, "update_password.html")
