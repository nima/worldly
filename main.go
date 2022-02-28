package main

import (
    "log"
    "net/http"
)

func main() {
    mux := http.NewServeMux()

    fileServer := http.FileServer(http.Dir("./static/"))
    mux.Handle("/static/", http.StripPrefix("/static", fileServer))

    log.Println("Starting server on :8080")
    err := http.ListenAndServe(":8080", mux)
    log.Fatal(err)
}
