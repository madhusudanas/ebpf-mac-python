package main

import "fmt"

//go:noinline
func add(x int, y int) {
	return x + y
}

func main() {
	fmt.Println(add(3, 4))
}
