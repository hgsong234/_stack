package main

import (
	"fmt"
	"net/http"
	"log"
)

// 루트 경로 ("/") 핸들러 함수
func homeHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Welcome to the home page!")
}

// "/hello" 경로 핸들러 함수
func helloHandler(w http.ResponseWriter, r *http.Request) {
	// URL 쿼리 파라미터에서 'name' 값을 가져온다.
	name := r.URL.Query().Get("name")
	if name == "" {
		name = "Guest"
	}
	fmt.Fprintf(w, "Hello, %s! How are you?", name)
}

func main() {
	// 라우터 등록
	http.HandleFunc("/", homeHandler)
	http.HandleFunc("/hello", helloHandler)

	// 서버 시작
	fmt.Println("Server is listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}