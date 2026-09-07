const main = (params) => {
    // Code here
    let vetor = [];
    for (let i = 0; i < 20; i++) {
        vetor.push(Math.floor(Math.random() * 100) + 1);
    }
    
    let min = Math.min(...vetor);
    let max = Math.max(...vetor);
    
    return [min, max]
}

console.log(main())