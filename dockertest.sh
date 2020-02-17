docker stop $(docker ps -a | grep "Exited" | awk '{print $1 }')
docker rm $(docker ps -a | grep "Exited" | awk '{print $1 }')
docker rmi $(docker images | grep "none" | awk '{print $3}')
docker build -t mypage-composer_chatbot . && docker run -it -p 3001:3001 mypage-composer_chatbot